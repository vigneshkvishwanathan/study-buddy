"""Root pytest config: command-line options shared by all tests."""


def pytest_addoption(parser):
    parser.addoption("--browser", default="chromium", choices=["chromium", "firefox", "webkit"],
                     help="Browser for Playwright UI tests")
    parser.addoption("--headed", action="store_true", help="Show the browser window")
