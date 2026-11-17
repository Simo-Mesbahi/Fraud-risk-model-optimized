"""Exercise the real public UI against a running API, including file round-trips."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_LABELS = {
    "Exploration": "Explore", "Data quality": "Data quality", "Time & evaluation splits": "Timeline",
    "Fraud patterns": "Fraud patterns", "Model experiments": "Models", "Investigation capacity": "Capacity",
    "Explainability & errors": "Errors", "Robustness & drift": "Robustness",
}
PAGES = ["Overview", "Data Science Lab", "Claim Analysis", "Portfolio Scoring", "Investigation Queue", "Model Insights", "System Status"]


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
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, accept_downloads=True, color_scheme="light")
        page.set_default_timeout(30000)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url)
        page.get_by_text("Scoring service operational", exact=True).wait_for(timeout=90000)

        def clean(target=page):
            expect(target.get_by_test_id("stApp")).to_have_attribute(
                "data-test-script-state", "notRunning", timeout=90000
            )
            expect(target.get_by_test_id("stException")).to_have_count(0)
            assert "Diagnostic reference:" not in target.locator("body").inner_text()

        def appearance(name, target=page):
            option = target.get_by_role("menuitemradio", name=name, exact=True)
            if not option.is_visible():
                target.get_by_role("button", name="Main menu", exact=True).click()
            try:
                option.click()
            except Exception:
                target.screenshot(path=str(args.output / "appearance-failure.png"))
                raise
            if name != "System":
                expect(target.locator("html")).to_have_attribute("data-fraud-theme", name.lower())
            # Streamlit deliberately keeps the menu open while comparing themes.
            target.keyboard.press("Escape")
            expect(target.get_by_role("menu", name="Main menu", exact=True)).not_to_be_visible()

        # Exercise the public native selector, including persistence and OS changes.
        expect(page.locator("html")).to_have_attribute("data-fraud-theme", "light")
        appearance("Dark")
        page.reload()
        page.get_by_role("heading", name="Executive Overview", exact=True).wait_for()
        expect(page.locator("html")).to_have_attribute("data-fraud-theme", "dark")
        appearance("System")
        expect(page.locator("html")).to_have_attribute("data-fraud-theme", "light")
        page.emulate_media(color_scheme="dark")
        expect(page.locator("html")).to_have_attribute("data-fraud-theme", "dark")
        page.emulate_media(color_scheme="light")
        expect(page.locator("html")).to_have_attribute("data-fraud-theme", "light")
        appearance("Dark")
        passed.extend(["appearance:native-selector", "appearance:reload-persistence",
                       "appearance:system-light", "appearance:system-dark", "appearance:system-live-update"])

        def navigate(name):
            page.get_by_test_id("stSidebar").get_by_role("link", name=name, exact=True).click()
            page.get_by_role("heading", name="Executive Overview" if name == "Overview" else name, exact=True, level=1).wait_for()
            clean()
            expect(page.get_by_test_id("stMain").locator("h1")).to_have_count(1)
            expect(page.get_by_test_id("stMain").locator("h1")).to_be_in_viewport()
            assert_header_clear(page)

        def assert_header_clear(target):
            assert target.locator(".app-topbar").evaluate(
                "e => e.getBoundingClientRect().top >= document.querySelector('[data-testid=stHeader]').getBoundingClientRect().bottom - 1"
            ), "Product context is hidden under the fixed header"

        def choose(label, option):
            if label == "Analysis workspace":
                page.get_by_test_id("stButtonGroup").get_by_text(WORKSPACE_LABELS[option], exact=True).click()
                return
            page.get_by_role("combobox", name=label, exact=True).click()
            page.get_by_role("option", name=option, exact=True).click()

        def sidebar_control(target, opening):
            selectors = ([
                '[data-testid="stExpandSidebarButton"]',
                '[data-testid="stExpandSidebarButton"] button',
                '[data-testid="stSidebarCollapsedControl"] button',
                'button[aria-label="Open sidebar"]',
                'button[aria-label="Expand sidebar"]',
            ] if opening else [
                '[data-testid="stSidebarCollapseButton"] button',
                'button[aria-label="Close sidebar"]',
            ])
            for selector in selectors:
                element = target.locator(selector)
                if element.count() and element.first.is_visible():
                    element.first.click()
                    return

        for name in PAGES:
            navigate(name)
            if name == "System Status":
                expect(page.locator(".metric-card-pro").filter(
                    has=page.get_by_text("System Status", exact=True)
                ).locator(".metric-value")).to_have_text("READY")
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
        page.get_by_text(workspaces["Exploration"], exact=True).wait_for()
        clean()
        page.screenshot(path=str(args.output / "science-desktop.png"), full_page=True)
        page.get_by_test_id("stVegaLiteChart").first.scroll_into_view_if_needed()
        page.screenshot(path=str(args.output / "science-charts-desktop.png"), full_page=True)

        navigate("Model Insights")
        for tab_name, heading in {
            "Performance": "Model Performance", "Explainability": "Global Explainability",
            "Errors & limits": "Observed Failure Modes", "Model contract": "Model Status",
        }.items():
            page.get_by_role("tab", name=tab_name, exact=True).click()
            page.get_by_role("heading", name=heading, exact=True, level=2).wait_for()
            clean()
            expect(page.get_by_test_id("stException")).to_have_count(0)
            passed.append("model-insights:" + tab_name)

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
        page.get_by_text("Explanation quality checks", exact=True).click()
        expect(page.locator(".metric-card-pro").filter(
            has=page.get_by_text("SHAP Additivity", exact=True)
        ).locator(".metric-value")).to_have_text("Verified")
        expect(page.locator(".metric-card-pro").filter(
            has=page.get_by_text("Feature Space", exact=True)
        ).locator(".metric-value")).to_have_text("107")
        appearance("Light")
        expect(page.get_by_role("heading", name="Model Explanation", exact=True)).to_be_visible()
        appearance("Dark")
        expect(page.get_by_role("heading", name="Model Explanation", exact=True)).to_be_visible()
        passed.append("appearance:preserves-scored-claim")
        page.screenshot(path=str(args.output / "claim-desktop.png"), full_page=True)
        passed.extend(["score-and-explain:quick-demo", "explanation:107-features-and-additivity"])

        navigate("Portfolio Scoring")
        page.get_by_role("tab", name="Upload Portfolio", exact=True).click()
        csv = pd.read_parquet(ROOT / "data/interim/claims.parquet").head(5).to_csv(index=False).encode()
        page.locator('input[type="file"]').first.set_input_files({"name": "verified-five-claims.csv", "mimeType": "text/csv", "buffer": csv})
        score = page.get_by_role("button", name="Score Portfolio", exact=True)
        expect(score).to_be_enabled()
        score.click()
        page.get_by_text("Portfolio Risk Overview", exact=True).wait_for()
        expect(page.locator(".metric-card-pro").filter(has=page.get_by_text("Claims Scored", exact=True)).locator(".metric-value")).to_have_text("5")
        clean()
        passed.append("portfolio:csv-upload-and-score")
        page.get_by_role("button", name="Continue to investigation", exact=True).click()
        page.get_by_role("button", name="Build queue from scored portfolio", exact=True).click()
        page.get_by_text("Queue Overview", exact=True).wait_for()
        clean()
        passed.append("portfolio:context-preserving-investigation-handoff")
        page.get_by_role("button", name="Reset Queue", exact=True).click()
        page.get_by_text("Build Investigation Queue", exact=True).wait_for()

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
        page.get_by_text("Pending review: 14 · Clear: 1", exact=True).wait_for()
        clean()
        resume = page.get_by_test_id("stFileUploader").filter(has_text="Resume decisions JSON")
        # Use the same native picker action as a user. This also waits for
        # Streamlit to finish rendering the current uploader after a rerun.
        with page.expect_file_chooser() as chosen:
            resume.get_by_role("button", name="Upload", exact=True).click()
        chosen.value.set_files(snapshot)
        expect(resume.get_by_text("decisions.json", exact=True)).to_be_visible(timeout=30000)
        restore = page.get_by_role("button", name="Restore decisions", exact=True)
        expect(restore).to_be_enabled(timeout=20000)
        restore.click()
        expect(page.get_by_test_id("stSelectbox").filter(has_text="Human decision").get_by_role("combobox", name="Human decision", exact=True)).to_have_value("Escalate")
        clean()
        passed.extend(["queue:score-and-rank", "queue:human-decision", "export:formula-safe-csv", "workspace:save-and-resume"])
        page.screenshot(path=str(args.output / "queue-desktop.png"), full_page=True)

        appearance("Light")
        for name in PAGES:
            navigate(name)
            page.screenshot(path=str(args.output / f"light-{name.lower().replace(' ', '-')}-desktop.png"), full_page=False)
            if name == "Data Science Lab":
                for workspace, title in workspaces.items():
                    choose("Analysis workspace", workspace)
                    page.get_by_text(title, exact=True).wait_for()
                    clean()
                    if page.get_by_test_id("stVegaLiteChart").count():
                        page.get_by_test_id("stVegaLiteChart").first.scroll_into_view_if_needed()
                    page.screenshot(path=str(args.output / f"light-science-{WORKSPACE_LABELS[workspace].lower().replace(' ', '-')}-desktop.png"), full_page=False)
                    passed.append("light-desktop:lab:" + workspace)
            passed.append("light-desktop:" + name)

        for width in [390, 768]:
            mobile = browser.new_page(viewport={"width": width, "height": 844}, is_mobile=True, has_touch=True, color_scheme="light")
            mobile.on("pageerror", lambda error: errors.append(str(error)))
            mobile.goto(args.url)
            mobile.get_by_role("heading", name="Executive Overview", level=1).wait_for(timeout=90000)
            for mode in ["Dark", "Light"]:
                appearance(mode, mobile)
                for name in PAGES:
                    nav = mobile.get_by_test_id("stSidebar").get_by_role("link", name=name, exact=True)
                    sidebar_control(mobile, True)
                    nav.click()
                    mobile.get_by_role("heading", name="Executive Overview" if name == "Overview" else name, exact=True, level=1).wait_for()
                    sidebar_control(mobile, False)
                    if width == 390:
                        expect(mobile.get_by_test_id("stSidebar")).not_to_be_in_viewport()
                    clean(mobile)
                    expect(mobile.get_by_test_id("stMain").locator("h1")).to_have_count(1)
                    expect(mobile.get_by_test_id("stMain").locator("h1")).to_be_in_viewport()
                    assert_header_clear(mobile)
                    assert mobile.evaluate("document.documentElement.scrollWidth <= innerWidth + 4"), f"Document overflow: {width}px {name}"
                    mobile.screenshot(path=str(args.output / f"{mode.lower()}-{name.lower().replace(' ', '-')}-{width}.png"), full_page=False)
                    if name == "Claim Analysis":
                        mobile.get_by_test_id("stRadioOption").filter(has=mobile.get_by_text("Quick Demo", exact=True)).click()
                        mobile.get_by_role("button", name="Analyze Demo Claim", exact=True).wait_for()
                        mobile.get_by_role("button", name="Analyze Demo Claim", exact=True).click()
                        mobile.get_by_text("Model Explanation", exact=True).wait_for()
                        clean(mobile)
                        mobile.screenshot(path=str(args.output / f"{mode.lower()}-claim-result-{width}.png"), full_page=False)
                        smart = mobile.get_by_test_id("stRadioOption").filter(has=mobile.get_by_text("Smart Analysis", exact=True))
                        smart.click()
                        mobile.get_by_role("combobox", name="Customer", exact=True).wait_for()
                        clean(mobile)
                        mobile.screenshot(path=str(args.output / f"{mode.lower()}-claim-intake-{width}.png"), full_page=False)
                    if name == "Data Science Lab":
                        for workspace, title in workspaces.items():
                            mobile.get_by_test_id("stButtonGroup").get_by_text(WORKSPACE_LABELS[workspace], exact=True).click()
                            mobile.get_by_text(title, exact=True).wait_for()
                            clean(mobile)
                            charts = mobile.get_by_test_id("stVegaLiteChart")
                            if charts.count():
                                for chart_index in range(charts.count()):
                                    chart = charts.nth(chart_index)
                                    chart.scroll_into_view_if_needed()
                                    assert chart.evaluate("e => e.scrollWidth <= e.clientWidth + 2"), f"Chart overflow: {width}px {workspace} chart {chart_index}"
                                    assert chart.evaluate("e => [...e.querySelectorAll('canvas, svg')].every(c => c.getBoundingClientRect().right <= innerWidth + 2)"), f"Cropped chart canvas: {width}px {workspace} chart {chart_index}"
                                    mobile.screenshot(path=str(args.output / f"{mode.lower()}-science-{WORKSPACE_LABELS[workspace].lower().replace(' ', '-')}-{width}-{chart_index}.png"), full_page=False)
                            else:
                                mobile.get_by_test_id("stDataFrame").first.scroll_into_view_if_needed()
                                mobile.screenshot(path=str(args.output / f"{mode.lower()}-science-{WORKSPACE_LABELS[workspace].lower().replace(' ', '-')}-{width}.png"), full_page=False)
                            assert mobile.evaluate("document.documentElement.scrollWidth <= innerWidth + 4")
                            passed.append(f"responsive:{mode.lower()}:{width}px:lab:{workspace}")
                    passed.append(f"responsive:{mode.lower()}:{width}px:{name}")
            mobile.close()
        assert not errors, errors
        browser.close()
    (args.output / "result.json").write_text(json.dumps({"passed": passed, "javascript_errors": errors}, indent=2))
    print(json.dumps({"passed_checks": len(passed), "javascript_errors": errors}))


if __name__ == "__main__":
    main()
