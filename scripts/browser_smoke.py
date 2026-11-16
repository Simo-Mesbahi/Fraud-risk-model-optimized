"""Exercise the real public UI against a running API, including file round-trips."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/browser")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    passed, errors = [], []
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = playwright.chromium.launch(**options)
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
        page.set_default_timeout(30000)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url)
        page.get_by_text("Scoring service operational", exact=True).wait_for(timeout=90000)

        def clean():
            expect(page.get_by_test_id("stException")).to_have_count(0)
            assert "Diagnostic reference:" not in page.locator("body").inner_text()

        def navigate(name):
            page.get_by_test_id("stSidebar").get_by_text(name, exact=True).click()
            page.get_by_test_id("stMain").get_by_text(name, exact=True).first.wait_for()
            clean()

        def choose(label, option):
            page.get_by_role("combobox", name=label, exact=True).click()
            page.get_by_role("option", name=option, exact=True).click()

        for name in ["Overview", "Data Science Lab", "Claim Analysis", "Portfolio Scoring", "Investigation Queue", "Model Insights", "System Status"]:
            navigate(name)
            passed.append("navigation:" + name)
        navigate("Data Science Lab")
        choose("Research corpus", "Expanded longitudinal research · 149,841 claims")
        workspaces = {
            "Exploration": "What does this portfolio contain?",
            "Data quality": "Which data issues are visible and how are they handled?",
            "Time & evaluation splits": "How do volume and outcomes change over time?",
            "Fraud patterns": "Which patterns distinguish the simulated labels?",
            "Model experiments": "What evidence supports the model and preprocessing choices?",
            "Investigation capacity": "What can investigators capture with limited capacity?",
            "Explainability & errors": "Where does the top-risk review policy make mistakes?",
            "Robustness & drift": "How stable are results across populations and time?",
        }
        for workspace in workspaces:
            choose("Analysis workspace", workspace)
            page.get_by_text(workspaces[workspace], exact=True).wait_for()
            expect(page.get_by_test_id("stMetric").first).to_be_visible()
            clean()
            passed.append("expanded-lab:" + workspace)
        choose("Analysis workspace", "Exploration")
        page.screenshot(path=str(args.output / "science-desktop.png"), full_page=True)

        navigate("Claim Analysis")
        # Streamlit overlays its native radio input with a styled option label.
        # Exercise the visible control, then assert the actual checked state.
        demo_option = page.get_by_test_id("stRadioOption").filter(
            has=page.get_by_text("Quick Demo", exact=True)
        )
        expect(demo_option).to_have_count(1)
        demo_option.click()
        expect(page.get_by_role("radio", name="Quick Demo", exact=True)).to_be_checked()
        page.get_by_role("button", name="Analyze Demo Claim", exact=True).click()
        page.get_by_text("Demo claim scored and explained successfully.", exact=True).wait_for()
        clean()
        page.screenshot(path=str(args.output / "claim-desktop.png"), full_page=True)
        passed.append("score-and-explain:quick-demo")

        navigate("Portfolio Scoring")
        csv = pd.read_parquet(ROOT / "data/interim/claims.parquet").head(5).to_csv(index=False).encode()
        page.locator('input[type="file"]').first.set_input_files({"name": "verified-five-claims.csv", "mimeType": "text/csv", "buffer": csv})
        score = page.get_by_role("button", name="Score Portfolio", exact=True)
        expect(score).to_be_enabled()
        score.click()
        page.get_by_text("Portfolio Risk Overview", exact=True).wait_for()
        expect(page.locator(".metric-card-pro").filter(has=page.get_by_text("Claims Scored", exact=True)).locator(".metric-value")).to_have_text("5")
        clean()
        passed.append("portfolio:csv-upload-and-score")

        navigate("Investigation Queue")
        page.get_by_role("tab", name="Demo Portfolio", exact=True).click()
        page.get_by_role("button", name="Build Demo Queue", exact=True).click()
        decision_select = page.get_by_test_id("stSelectbox").filter(has_text="Human decision")
        expect(decision_select).to_have_count(1)
        decision_select.get_by_role("combobox", name="Human decision", exact=True).wait_for()
        decision_select.get_by_role("combobox", name="Human decision", exact=True).click()
        decision_select.get_by_role("combobox", name="Human decision", exact=True).fill("Escalate")
        decision_select.get_by_role("combobox", name="Human decision", exact=True).press("Enter")
        expect(decision_select.get_by_role("combobox", name="Human decision", exact=True)).to_have_value("Escalate")
        page.get_by_role("textbox", name="Investigation note", exact=True).fill("=1+1; synthetic browser verification")
        page.get_by_role("button", name="Save Human Decision", exact=True).click()
        page.get_by_text("Last saved decision:", exact=False).wait_for()
        clean()
        with page.expect_download() as downloaded:
            page.get_by_role("button", name="Download Investigation Queue", exact=True).click()
        queue_path = args.output / "queue.csv"
        downloaded.value.save_as(queue_path)
        assert "'=1+1" in queue_path.read_text(encoding="utf-8-sig")
        page.get_by_text("Save & resume investigator decisions", exact=True).click()
        with page.expect_download() as downloaded:
            page.get_by_role("button", name="Save investigator decisions", exact=True).click()
        snapshot = args.output / "decisions.json"
        downloaded.value.save_as(snapshot)
        assert json.loads(snapshot.read_text())["decisions"][0]["decision"] == "Escalate"
        decision_select.get_by_role("combobox", name="Human decision", exact=True).click()
        decision_select.get_by_role("combobox", name="Human decision", exact=True).fill("Clear")
        decision_select.get_by_role("combobox", name="Human decision", exact=True).press("Enter")
        expect(decision_select.get_by_role("combobox", name="Human decision", exact=True)).to_have_value("Clear")
        page.get_by_role("button", name="Save Human Decision", exact=True).click()
        resume = page.get_by_test_id("stFileUploader").filter(has_text="Resume decisions JSON")
        resume.locator('input[type="file"]').set_input_files(snapshot)
        restore = page.get_by_role("button", name="Restore decisions", exact=True)
        expect(restore).to_be_enabled(timeout=15000)
        restore.click()
        expect(page.get_by_test_id("stSelectbox").filter(has_text="Human decision").get_by_role("combobox", name="Human decision", exact=True)).to_have_value("Escalate")
        clean()
        passed.extend(["queue:score-and-rank", "queue:human-decision", "export:formula-safe-csv", "workspace:save-and-resume"])
        page.screenshot(path=str(args.output / "queue-desktop.png"), full_page=True)

        mobile = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        mobile.goto(args.url)
        mobile.get_by_text("Scoring service operational", exact=True).wait_for(timeout=90000)
        for selector in ['[data-testid="stExpandSidebarButton"] button', '[data-testid="stSidebarCollapsedControl"] button', 'button[aria-label="Open sidebar"]']:
            control = mobile.locator(selector)
            if control.count() and control.first.is_visible():
                control.first.click()
                break
        mobile.get_by_test_id("stSidebar").get_by_text("Data Science Lab", exact=True).click()
        for selector in ['[data-testid="stSidebarCollapseButton"] button', 'button[aria-label="Close sidebar"]']:
            control = mobile.locator(selector)
            if control.count() and control.first.is_visible():
                control.first.click()
                break
        expect(mobile.get_by_role("combobox", name="Analysis workspace", exact=True)).to_be_visible()
        assert mobile.evaluate("document.documentElement.scrollWidth <= innerWidth + 4"), "Mobile document overflow"
        expect(mobile.get_by_test_id("stException")).to_have_count(0)
        mobile.screenshot(path=str(args.output / "science-mobile.png"), full_page=True)
        passed.append("mobile:390px-navigation-and-no-document-overflow")
        assert not errors, errors
        browser.close()
    (args.output / "result.json").write_text(json.dumps({"passed": passed, "javascript_errors": errors}, indent=2))
    print(json.dumps({"passed_checks": len(passed), "javascript_errors": errors}))


if __name__ == "__main__":
    main()
