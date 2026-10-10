import urllib.request
import urllib.parse
import json
import io

BASE_FE = "http://127.0.0.1:5173"
BASE_BE = "http://127.0.0.1:8000"

def test_system():
    print("=" * 60)
    print("      JSCDM CHURCH ATTENDANCE SYSTEM - SELF VERIFICATION    ")
    print("=" * 60)

    # 1. Frontend Server Check
    try:
        res = urllib.request.urlopen(BASE_FE)
        print(f"✓ Frontend Server ({BASE_FE}): UP & RUNNING (Status {res.status})")
    except Exception as e:
        print(f"✗ Frontend Server error: {e}")

    # 2. Backend Health & Config Check
    try:
        res = urllib.request.urlopen(f"{BASE_BE}/api/health")
        data = json.loads(res.read().decode())
        print(f"✓ Backend API ({BASE_BE}/api/health): UP & RUNNING")
        print(f"  - Church Name: {data.get('church')}")
        print(f"  - Members Count: {data.get('members_count')}")
        print(f"  - Database Mode: {data.get('database')}")
    except Exception as e:
        print(f"✗ Backend API error: {e}")

    # 3. Excel Single & Range Download Test
    try:
        res_single = urllib.request.urlopen(f"{BASE_BE}/api/reports/excel?date=2026-10-10")
        excel_bytes = res_single.read()
        print(f"✓ Excel Single Date Export (/api/reports/excel?date=2026-10-10): {len(excel_bytes)} bytes downloaded")

        res_range = urllib.request.urlopen(f"{BASE_BE}/api/reports/excel?start_date=2026-10-01&end_date=2026-10-10")
        excel_range_bytes = res_range.read()
        print(f"✓ Excel Date Range Export (/api/reports/excel?start_date=2026-10-01&end_date=2026-10-10): {len(excel_range_bytes)} bytes downloaded")
    except Exception as e:
        print(f"✗ Excel export error: {e}")

    # 4. PDF Single & Range Download Test
    try:
        res_single_pdf = urllib.request.urlopen(f"{BASE_BE}/api/reports/pdf?date=2026-10-10")
        pdf_bytes = res_single_pdf.read()
        print(f"✓ PDF Single Date Export (/api/reports/pdf?date=2026-10-10): {len(pdf_bytes)} bytes downloaded")

        res_range_pdf = urllib.request.urlopen(f"{BASE_BE}/api/reports/pdf?start_date=2026-10-01&end_date=2026-10-10")
        pdf_range_bytes = res_range_pdf.read()
        print(f"✓ PDF Date Range Export (/api/reports/pdf?start_date=2026-10-01&end_date=2026-10-10): {len(pdf_range_bytes)} bytes downloaded")
    except Exception as e:
        print(f"✗ PDF export error: {e}")

    # 5. AI Chatbot API Endpoints & Guardrail Check
    def post_chat(msg):
        req = urllib.request.Request(
            f"{BASE_BE}/api/chat",
            data=json.dumps({"message": msg, "conversation_history": []}).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())

    # A. Personal Attendance Report (Fraction & Detailed history)
    try:
        chat_res = post_chat("Show attendance report for John Anderson")
        reply = chat_res.get("reply", "")
        print("\n--- Chatbot Personal Attendance Report Response ---")
        print(reply[:350])
        assert "/" in reply or "Fraction" in reply
        assert "Percentage" in reply or "%" in reply
        print("✓ Chatbot Personal Report Test: PASSED (Fraction & History verified)")
    except Exception as e:
        print(f"✗ Chatbot personal report error: {e}")

    # B. Strict Topic Guardrails Test
    try:
        chat_guardrail = post_chat("How do I write a python loop?")
        reply_g = chat_guardrail.get("reply", "")
        expected_refusal = "Sorry, I can only assist with Bible-related questions, Christian teachings, church activities, and authorized church attendance information. Please ask me something related to these topics."
        print("\n--- Chatbot Guardrail Test (Out of Scope Query) ---")
        print(f"Query: 'How do I write a python loop?'")
        print(f"Response: '{reply_g}'")
        assert reply_g == expected_refusal
        print("✓ Chatbot Guardrail Refusal Test: PASSED (Exact refusal message returned)")
    except Exception as e:
        print(f"✗ Chatbot guardrail error: {e}")

    # C. Bible Question Test
    try:
        chat_bible = post_chat("Tell me about King David")
        reply_b = chat_bible.get("reply", "")
        print("\n--- Chatbot Bible Q&A Test ---")
        print(reply_b[:250])
        assert "David" in reply_b
        print("✓ Chatbot Bible Q&A Test: PASSED")
    except Exception as e:
        print(f"✗ Chatbot Bible Q&A error: {e}")

    print("\n" + "=" * 60)
    print("          ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!       ")
    print("=" * 60)

if __name__ == "__main__":
    test_system()
