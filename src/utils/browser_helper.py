"""浏览器辅助工具 - 使用 Selenium 处理 JavaScript 反爬虫"""

import logging
from typing import Optional
import time

logger = logging.getLogger(__name__)


def fetch_with_selenium(url: str, timeout: int = 15) -> Optional[str]:
    """
    使用 Selenium 获取页面内容（用于处理 JavaScript 反爬虫）
    
    Args:
        url: 要获取的 URL
        timeout: 超时时间（秒）
        
    Returns:
        页面 HTML 内容，如果失败返回 None
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.common.exceptions import TimeoutException, WebDriverException
        from webdriver_manager.chrome import ChromeDriverManager
        
        # 配置无头浏览器（GitHub Actions 环境）
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        logger.info(f"使用 Selenium 获取页面: {url[:80]}...")
        
        driver = None
        try:
            # 自动下载并使用正确版本的 ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(timeout)
            
            # 打开页面
            driver.get(url)
            
            # 等待页面加载完成（等待 body 元素）
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 额外等待 2 秒确保 JavaScript 执行完毕
            time.sleep(2)
            
            # 获取页面源代码
            html = driver.page_source
            
            logger.info(f"✓ Selenium 成功获取页面内容 ({len(html)} 字节)")
            return html
            
        except TimeoutException:
            logger.warning(f"Selenium 超时: {url}")
            return None
        except WebDriverException as e:
            logger.warning(f"Selenium WebDriver 错误: {e}")
            return None
        except Exception as e:
            logger.warning(f"Selenium 获取页面失败: {e}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                    
    except ImportError:
        logger.warning("未安装 selenium 或 webdriver-manager，跳过 Selenium 获取")
        return None
    except Exception as e:
        logger.warning(f"Selenium 初始化失败: {e}")
        return None


def fetch_with_javascript_execution(url: str, timeout: int = 15) -> Optional[str]:
    """
    使用 Selenium 执行 JavaScript 后获取页面内容
    
    Args:
        url: 要获取的 URL
        timeout: 超时时间（秒）
        
    Returns:
        页面 HTML 内容，如果失败返回 None
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.common.exceptions import TimeoutException, JavascriptException
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(timeout)
        
        try:
            driver.get(url)
            
            # 执行 JavaScript 滚动页面（某些网站会这样加载内容）
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 再次滚回顶部
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            return driver.page_source
            
        finally:
            driver.quit()
            
    except Exception as e:
        logger.warning(f"JavaScript 执行失败: {e}")
        return None
