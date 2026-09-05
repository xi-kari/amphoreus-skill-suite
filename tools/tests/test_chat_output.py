"""Check the evidence scanner, independently of live model acceptance runs."""

import json
import tempfile
import unittest
from pathlib import Path

from check_chat_output import check_case


class ChatOutputChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.case = {'id': 'sample', 'prompt': '陪我聊一会', 'mode': 'chat',
                     'expected_speakers': [], 'min_images': 0, 'max_images': 1}

    def check(self, final, messages=(), extra_events=()):
        (self.directory / 'sample-final.md').write_text(final, encoding='utf-8')
        events = [{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': text}}
                  for text in messages]
        events.extend(extra_events)
        (self.directory / 'sample-events.jsonl').write_text(
            '\n'.join(json.dumps(event, ensure_ascii=False) for event in events), encoding='utf-8')
        return check_case(self.case, self.directory)

    def test_progress_leak_is_not_hidden_by_clean_final(self):
        result = self.check('我们坐一会儿吧。', ['我先读取角色设定文件。'])
        self.assertFalse(result['mechanical_pass'])
        self.assertTrue(any(row['rule'] == 'backstage_read' for row in result['findings']))

    def test_folded_ledger_is_visible_output(self):
        result = self.check('晚安。\n<details><summary>台账</summary>读取：common.md</details>')
        self.assertFalse(result['mechanical_pass'])
        self.assertTrue(any(row['rule'] == 'folded_metadata' for row in result['findings']))

    def test_skill_notice_and_identifier_are_visible_process_language(self):
        for prelude in ('这次就用 amphoreus-anaxa。', '用你指定的三月七技能陪你聊聊。'):
            with self.subTest(prelude=prelude):
                result = self.check('好呀，慢慢聊。', [prelude])
                self.assertFalse(result['mechanical_pass'])

    def test_skill_id_in_image_path_is_not_a_process_notice(self):
        result = self.check('晚安。\n![昔涟](<C:/skills/amphoreus/assets/stickers/cyrene.webp>)')
        self.assertTrue(result['mechanical_pass'])

    def test_actual_audit_topic_is_allowed_without_own_process(self):
        self.case['prompt'] = '朋友做审计，买菜清单也叫台账，真有趣。'
        self.assertTrue(self.check('那份买菜台账上，会不会还有一栏专门记小零食？')['mechanical_pass'])

    def test_explicit_source_question_is_marked_for_semantic_review(self):
        self.case.update(mode='source', prompt='你实际读过哪些文件？')
        result = self.check('上一轮读过 common.md；这轮没有重新读取。')
        self.assertTrue(result['mechanical_pass'])
        self.assertTrue(any('actual tool events' in row for row in result['semantic_review']))

    def test_tool_data_and_reasoning_are_not_assistant_announcements(self):
        events = [
            {'type': 'item.completed', 'item': {'type': 'reasoning', 'text': '台账'}},
            {'type': 'item.completed', 'item': {'type': 'command_execution', 'aggregated_output': 'common.md'}},
        ]
        self.assertTrue(self.check('好呀，今天想聊什么？', extra_events=events)['mechanical_pass'])

    def test_missing_event_log_cannot_prove_a_clean_conversation(self):
        (self.directory / 'sample-final.md').write_text('晚安。', encoding='utf-8')
        result = check_case(self.case, self.directory)
        self.assertFalse(result['mechanical_pass'])
        self.assertTrue(any(row['rule'] == 'missing_events' for row in result['findings']))


if __name__ == '__main__':
    unittest.main()
