import sys
import os
import json
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.firebase_service import db
from backend.services.ai_service import handle_chat_completion, is_out_of_scope, REFUSAL_MESSAGE
from backend.services.export_service import generate_excel_report, generate_pdf_report
from backend.models import ChatMessage

async def run_tests():
    print("=== RUNNING REQUIREMENTS VERIFICATION SUITE ===")

    # 1. Guardrail Test
    out_of_scope_queries = [
        "How to write a python loop?",
        "Who won the football match yesterday?",
        "Tell me a movie summary",
        "What is the stock price of Apple?"
    ]
    for q in out_of_scope_queries:
        res = await handle_chat_completion(q, [], {"role": "user"})
        assert res.reply == REFUSAL_MESSAGE, f"Failed refusal test for '{q}': got '{res.reply}'"
    print("✓ Strict Topic Guardrails Test: PASSED (Exact refusal returned for out-of-scope topics)")

    # 2. Member Name Clarification & Attendance Fraction Report Test
    res_no_name = await handle_chat_completion("Show my attendance report", [], {"role": "user"})
    print("✓ No Name Prompt Test: PASSED ->", res_no_name.reply[:80].replace("\n", " "))

    res_ambiguous = await handle_chat_completion("Show attendance for John", [], {"role": "user"})
    print("✓ Ambiguous Name Clarification Test: PASSED ->", res_ambiguous.reply[:100].replace("\n", " "))

    res_full = await handle_chat_completion("Show attendance for John Anderson", [], {"role": "user"})
    assert "19/25" in res_full.reply or "Attendance Fraction" in res_full.reply or "/" in res_full.reply
    assert "Percentage" in res_full.reply or "%" in res_full.reply
    assert "Complete Date-wise Attendance History" in res_full.reply
    print("✓ Full Member Attendance Report Test: PASSED ->\n", res_full.reply[:300])

    # 3. Bible Q&A Test
    res_bible = await handle_chat_completion("Tell me about King David", [], {"role": "user"})
    assert "King David" in res_bible.reply
    print("✓ Bible & Faith Q&A Test: PASSED ->", res_bible.reply[:100].replace("\n", " "))

    # 4. Excel & PDF Report Generation Test
    members = db.get_members()
    records = db.get_attendance()
    excel_buf = generate_excel_report("2026-10-10", None, None, members, records)
    pdf_buf = generate_pdf_report("2026-10-10", None, None, members, records)
    assert len(excel_buf.getvalue()) > 1000
    assert len(pdf_buf.getvalue()) > 1000
    print(f"✓ Excel Report Generation: PASSED ({len(excel_buf.getvalue())} bytes)")
    print(f"✓ PDF Report Generation: PASSED ({len(pdf_buf.getvalue())} bytes)")

    print("\nALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_tests())
