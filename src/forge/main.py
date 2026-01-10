from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        # 默认使用 chromium，这是 Playwright 自带的独立浏览器，
        # 不会影响你系统安装的 Chrome，是最安全、最推荐的方式。
        browser = p.chromium.launch(headless=False)
        
        # 如果你非要使用系统安装的 Google Chrome，可以使用 channel="chrome"
        # 只要你系统里装了 Chrome，就不需要运行 install --force
        # browser = p.chromium.launch(channel="chrome", headless=False)
        
        page = browser.new_page()
        page.goto("https://example.com")
        print(f"Title: {page.title()}")
        browser.close()

if __name__ == "__main__":
    main()
