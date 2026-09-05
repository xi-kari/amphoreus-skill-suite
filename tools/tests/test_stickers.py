"""Exercise portable sticker selection and byte-for-byte packaging."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_SKILL = ROOT / "skills/amphoreus"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runtime = load_module("sticker_runtime", SOURCE_SKILL / "scripts/stickers.py")
packager = load_module("sticker_packager", ROOT / "tools/package_stickers.py")


class StickerSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="amphoreus-stickers-")
        self.addCleanup(self.temp.cleanup)
        self.skill = Path(self.temp.name) / "中文 空格安装" / "amphoreus"
        self.assets = self.skill / "assets/stickers"
        shutil.copytree(SOURCE_SKILL / "assets/stickers", self.assets)
        (self.skill / "scripts").mkdir()
        shutil.copyfile(SOURCE_SKILL / "scripts/stickers.py", self.skill / "scripts/stickers.py")
        self.catalog = json.loads((self.assets / "manifest.json").read_text(encoding="utf-8"))

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, "-B", str(self.skill / "scripts/stickers.py"), *arguments],
            cwd=self.temp.name, capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def test_every_speaker_has_an_existing_own_default_after_relocation(self):
        expected = {
            "aglaea", "anaxa", "castorice", "cerydra", "cipher", "cyrene", "hyacine",
            "hysilens", "march7th", "march7th-evernight", "mydei", "phainon", "terrae",
            "trailblazer-caelus", "trailblazer-stelle", "tribbie", "tribbie-an", "tribbie-ning",
            "chimera-mydei", "chimera-terrae", "chimera-cerydra", "chimera-hysilens",
            "chimera-phainon", "chimera-tribbie", "chimera-cipher", "chimera-castorice",
            "chimera-anaxa", "chimera-march7th", "chimera-aglaea", "chimera-hyacine",
            "cyrene-young", "mimi",
        }
        self.assertEqual(expected, {row["key"] for row in self.catalog["speakers"]})
        for speaker in expected:
            with self.subTest(speaker=speaker):
                result = runtime.select(self.catalog, self.assets, speaker)
                default = {"cyrene-young": "cyrene-young-hehe", "mimi": "mimi-hug"}.get(speaker, speaker)
                self.assertEqual("ok", result["status"])
                self.assertEqual(default, result["key"])
                self.assertEqual(speaker, result["speaker"])
                self.assertTrue(Path(result["path"]).is_file())
                self.assertTrue(Path(result["path"]).is_relative_to(self.skill.resolve()))
                fallback = runtime.select(self.catalog, self.assets, speaker, mood="没有这张表情")
                self.assertEqual(("fallback", default), (fallback["status"], fallback["key"]))

    def test_chinese_cli_uses_installed_absolute_path_with_safe_markdown(self):
        proc = self.run_cli("--speaker", "昔涟", "--mood", "收到", "--format", "json")
        self.assertEqual(0, proc.returncode, proc.stderr)
        result = json.loads(proc.stdout)
        expected = (self.assets / "cyrene-roger.webp").resolve().as_posix()
        self.assertEqual(expected, result["path"])
        self.assertEqual(f"![昔涟·收到](<{expected}>)", result["markdown"])
        self.assertIn("中文 空格安装", result["markdown"])
        markdown = self.run_cli("--speaker", "cyrene", "--mood", "收到")
        self.assertEqual(result["markdown"], markdown.stdout.strip())

    def test_variants_and_companions_never_leak_through_owner(self):
        pairs = [
            ("三月七", "march7th-evernight-warning"), ("长夜月", "march7th"),
            ("缇宝", "tribbie-an-goodnight"), ("缇安", "tribbie-ning-send"),
            ("昔涟", "cyrene-young-hehe"), ("风堇", "mimi-hug"),
            ("万敌", "chimera-mydei"), ("迷迷", "hyacine-heal"),
        ]
        for speaker, key in pairs:
            with self.subTest(speaker=speaker, key=key):
                result = runtime.select(self.catalog, self.assets, speaker, key=key)
                self.assertEqual(("error", "speaker_mismatch", ""),
                                 (result["status"], result["reason"], result["markdown"]))
        self.assertEqual("march7th", runtime.select(self.catalog, self.assets, "三月七", mood="警告")["key"])
        self.assertEqual("tribbie", runtime.select(self.catalog, self.assets, "缇宝", mood="晚安")["key"])
        self.assertEqual("cyrene", runtime.select(self.catalog, self.assets, "昔涟", mood="嘻嘻")["key"])
        self.assertEqual("hyacine", runtime.select(self.catalog, self.assets, "风堇", mood="抱")["key"])

    def test_explicit_variant_and_companion_names_choose_their_own_images(self):
        cases = [
            ("长夜月", "警告", "march7th-evernight-warning"),
            ("缇安", "晚安", "tribbie-an-goodnight"),
            ("缇宁", "发送", "tribbie-ning-send"),
            ("小昔涟", "嘻嘻", "cyrene-young-hehe"),
            ("迷迷", "抱", "mimi-hug"),
            ("蜜果羹", "再战", "chimera-mydei"),
        ]
        for speaker, mood, key in cases:
            with self.subTest(speaker=speaker):
                self.assertEqual(key, runtime.select(self.catalog, self.assets, speaker, mood=mood)["key"])

    def test_invalid_keys_and_unknown_speakers_produce_no_image(self):
        for arguments in [
            ("--speaker", "昔涟", "--key", "../../cyrene"),
            ("--speaker", "昔涟", "--key", "not-a-sticker"),
            ("--speaker", "不存在的角色"),
            ("--speaker", "昔涟", "--key", "cyrene-young-hehe"),
        ]:
            with self.subTest(arguments=arguments):
                proc = self.run_cli(*arguments)
                self.assertEqual(2, proc.returncode)
                self.assertEqual("", proc.stdout)
                self.assertTrue(proc.stderr.strip())

    def test_missing_selected_file_falls_back_then_missing_default_omits(self):
        (self.assets / "cyrene-roger.webp").unlink()
        result = runtime.select(self.catalog, self.assets, "昔涟", key="cyrene-roger")
        self.assertEqual(("fallback", "missing_file", "cyrene"),
                         (result["status"], result["reason"], result["key"]))
        (self.assets / "cyrene.webp").unlink()
        result = runtime.select(self.catalog, self.assets, "昔涟", mood="收到")
        self.assertEqual(("omitted", "missing_default", ""),
                         (result["status"], result["reason"], result["markdown"]))
        proc = self.run_cli("--speaker", "昔涟", "--mood", "收到")
        self.assertEqual((0, ""), (proc.returncode, proc.stdout))

    def test_missing_catalog_is_optional_presentation_failure(self):
        (self.assets / "manifest.json").unlink()
        proc = self.run_cli("--speaker", "昔涟")
        self.assertEqual((0, ""), (proc.returncode, proc.stdout))
        data = json.loads(self.run_cli("--speaker", "昔涟", "--format", "json").stdout)
        self.assertEqual(("omitted", "catalog_unavailable"), (data["status"], data["reason"]))

    def test_listing_contains_only_existing_images_of_actual_speaker(self):
        (self.assets / "tribbie-wise.webp").unlink()
        proc = self.run_cli("--speaker", "缇宝", "--list", "--format", "json")
        self.assertEqual(0, proc.returncode, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual({"tribbie", "tribbie-boom"}, {row["key"] for row in result["items"]})
        self.assertTrue(all(row["speaker"] == "tribbie" for row in result["items"]))

    def test_array_catalog_is_omitted_without_traceback(self):
        (self.assets / "manifest.json").write_text("[]", encoding="utf-8")
        proc = self.run_cli("--speaker", "昔涟", "--format", "json")
        self.assertEqual(0, proc.returncode)
        result = json.loads(proc.stdout)
        self.assertEqual(("omitted", "catalog_unavailable", ""),
                         (result["status"], result["reason"], result["markdown"]))
        self.assertNotIn("Traceback", proc.stderr)

    def test_non_string_alias_is_omitted_without_traceback(self):
        self.catalog["speakers"][0]["aliases"] = [1]
        (self.assets / "manifest.json").write_text(json.dumps(self.catalog), encoding="utf-8")
        proc = self.run_cli("--speaker", "昔涟", "--format", "json")
        self.assertEqual(0, proc.returncode)
        result = json.loads(proc.stdout)
        self.assertEqual(("omitted", "catalog_unavailable", ""),
                         (result["status"], result["reason"], result["markdown"]))
        self.assertNotIn("Traceback", proc.stderr)

    def test_catalog_path_cannot_escape_installed_assets(self):
        outside = self.skill / "outside.webp"
        outside.write_bytes(b"outside")
        row = next(row for row in self.catalog["items"] if row["key"] == "cyrene-roger")
        row["file"] = "../../outside.webp"
        result = runtime.select(self.catalog, self.assets, "昔涟", key="cyrene-roger")
        self.assertEqual("cyrene", result["key"])
        self.assertNotIn("outside", result["markdown"])


class StickerPackageTests(unittest.TestCase):
    def test_package_matches_all_canonical_image_bytes_and_index(self):
        self.assertEqual([], packager.package(ROOT, check=True))
        catalog = json.loads((ROOT / packager.ASSETS / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(96, len(catalog["items"]))
        for row in catalog["items"]:
            with self.subTest(key=row["key"]):
                self.assertEqual((ROOT / "assets/stickers/w" / row["file"]).read_bytes(),
                                 (ROOT / packager.ASSETS / row["file"]).read_bytes())

    def test_check_detects_missing_stale_and_orphan_without_writing(self):
        with tempfile.TemporaryDirectory(prefix="amphoreus-package-") as temp:
            root = Path(temp)
            source = root / "assets/stickers"
            source.mkdir(parents=True)
            shutil.copyfile(ROOT / "assets/stickers/manifest.json", source / "manifest.json")
            shutil.copytree(ROOT / "assets/stickers/w", source / "w")
            packager.package(root)
            images = root / packager.ASSETS
            missing = images / "cyrene.webp"
            missing.unlink()
            stale = images / "tribbie.webp"
            stale.write_bytes(b"stale")
            orphan = images / "orphan.webp"
            orphan.write_bytes(b"orphan")
            index = root / packager.INDEX
            index.write_text("stale index", encoding="utf-8")
            differences = packager.package(root, check=True)
            self.assertEqual(4, len(differences))
            self.assertFalse(missing.exists())
            self.assertEqual(b"stale", stale.read_bytes())
            self.assertTrue(orphan.exists())
            self.assertEqual("stale index", index.read_text(encoding="utf-8"))
            packager.package(root)
            self.assertEqual([], packager.package(root, check=True))
            self.assertFalse(orphan.exists())

    def test_unknown_companion_requires_explicit_identity_mapping(self):
        source = json.loads((ROOT / "assets/stickers/manifest.json").read_text(encoding="utf-8"))
        source["items"].append({"key": "unknown-pet", "owner": "cyrene", "note": "伙伴", "kind": "companion"})
        with self.assertRaisesRegex(ValueError, "Unmapped companion"):
            packager.make_catalog(source)


if __name__ == "__main__":
    unittest.main()
