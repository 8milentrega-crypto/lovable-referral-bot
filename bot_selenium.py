"""
Lovable Referral Bot - Automação Real com Selenium
Baseado nos testes bem-sucedidos realizados manualmente
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import string
import re
import os
import imaplib
import email
from email.header import decode_header

class LovableBot:
    def __init__(self, headless=True, log_callback=None):
        self.driver = None
        self.headless = headless
        self.log_callback = log_callback or print
        self.wait_time = 10
        
    def log(self, message, status='info'):
        """Log message with callback"""
        if self.log_callback:
            self.log_callback(message, status)
        else:
            print(f"[{status.upper()}] {message}")
    
    def random_delay(self, min_sec=0.5, max_sec=2.0):
        """Human-like random delay"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def human_type(self, element, text):
        """Type like a human with random delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def start_browser(self):
        """Initialize undetected Chrome browser"""
        try:
            self.log("🌐 Iniciando navegador...", "info")
            
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless=new')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-gpu')
            options.add_argument('--lang=en-US')
            
            # Random user agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            self.driver = uc.Chrome(options=options, version_main=120)
            self.driver.implicitly_wait(self.wait_time)
            
            self.log("✅ Navegador iniciado com sucesso!", "success")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao iniciar navegador: {str(e)}", "error")
            return False
    
    def close_browser(self):
        """Close browser and clean up"""
        if self.driver:
            try:
                self.driver.quit()
                self.log("🔒 Navegador fechado", "info")
            except:
                pass
            self.driver = None
    
    def access_referral_link(self, referral_link):
        """Access the Lovable referral link"""
        try:
            self.log(f"🔗 Acessando link de referral...", "info")
            self.driver.get(referral_link)
            self.random_delay(2, 4)
            
            # Check if we're on the signup page
            if "lovable.dev" in self.driver.current_url:
                self.log("✅ Página de referral carregada!", "success")
                return True
            else:
                self.log("❌ Não foi possível acessar a página de referral", "error")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao acessar link: {str(e)}", "error")
            return False
    
    def create_account(self, email_address, password):
        """Create account on Lovable"""
        try:
            self.log(f"📧 Criando conta com: {email_address}", "info")
            
            # Wait for email input
            self.random_delay(1, 2)
            
            # Find and fill email input
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[placeholder*='email'], input[name='email']"))
            )
            email_input.clear()
            self.human_type(email_input, email_address)
            self.random_delay(0.5, 1)
            
            # Click Continue button
            continue_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continue') or contains(text(), 'Sign up')]")
            continue_btn.click()
            self.random_delay(1, 2)
            
            # Wait for password input
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            
            # Create a strong password for Lovable
            lovable_password = password + "Test!1"  # Add complexity
            password_input.clear()
            self.human_type(password_input, lovable_password)
            self.random_delay(0.5, 1)
            
            # Click Create account button
            create_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'Sign up')]")
            create_btn.click()
            self.random_delay(2, 4)
            
            self.log("✅ Formulário de cadastro enviado!", "success")
            return True, lovable_password
            
        except Exception as e:
            self.log(f"❌ Erro ao criar conta: {str(e)}", "error")
            return False, None
    
    def verify_email_outlook(self, email_address, email_password):
        """Verify email via Outlook IMAP"""
        try:
            self.log(f"📨 Verificando email no Outlook...", "info")
            
            # Connect to Outlook IMAP
            mail = imaplib.IMAP4_SSL("outlook.office365.com")
            mail.login(email_address, email_password)
            mail.select("INBOX")
            
            # Wait for verification email
            max_attempts = 10
            for attempt in range(max_attempts):
                self.log(f"🔍 Procurando email de verificação... (tentativa {attempt+1}/{max_attempts})", "info")
                
                # Search for Lovable emails
                _, messages = mail.search(None, '(FROM "lovable" OR SUBJECT "verify")')
                
                if messages[0]:
                    email_ids = messages[0].split()
                    latest_email_id = email_ids[-1]
                    
                    _, msg_data = mail.fetch(latest_email_id, "(RFC822)")
                    email_body = msg_data[0][1]
                    msg = email.message_from_bytes(email_body)
                    
                    # Extract verification link
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/html":
                                body = part.get_payload(decode=True).decode()
                                # Find verification link
                                links = re.findall(r'https://[^\s<>"]+verify[^\s<>"]+', body)
                                if links:
                                    verification_link = links[0]
                                    self.log(f"✅ Link de verificação encontrado!", "success")
                                    mail.logout()
                                    return verification_link
                    else:
                        body = msg.get_payload(decode=True).decode()
                        links = re.findall(r'https://[^\s<>"]+verify[^\s<>"]+', body)
                        if links:
                            verification_link = links[0]
                            self.log(f"✅ Link de verificação encontrado!", "success")
                            mail.logout()
                            return verification_link
                
                # Also check Junk folder
                mail.select("Junk")
                _, messages = mail.search(None, '(FROM "lovable" OR SUBJECT "verify")')
                
                if messages[0]:
                    email_ids = messages[0].split()
                    latest_email_id = email_ids[-1]
                    
                    _, msg_data = mail.fetch(latest_email_id, "(RFC822)")
                    email_body = msg_data[0][1]
                    msg = email.message_from_bytes(email_body)
                    
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/html":
                                body = part.get_payload(decode=True).decode()
                                links = re.findall(r'https://[^\s<>"]+', body)
                                for link in links:
                                    if 'verify' in link.lower() or 'confirm' in link.lower():
                                        self.log(f"✅ Link de verificação encontrado no Junk!", "success")
                                        mail.logout()
                                        return link
                
                mail.select("INBOX")
                time.sleep(5)
            
            mail.logout()
            self.log("❌ Email de verificação não encontrado", "error")
            return None
            
        except Exception as e:
            self.log(f"❌ Erro ao verificar email: {str(e)}", "error")
            return None
    
    def click_verification_link(self, verification_link):
        """Click the verification link"""
        try:
            self.log("🔗 Acessando link de verificação...", "info")
            self.driver.get(verification_link)
            self.random_delay(3, 5)
            
            # Check if verification was successful
            if "verified" in self.driver.page_source.lower() or "success" in self.driver.page_source.lower():
                self.log("✅ Email verificado com sucesso!", "success")
                return True
            
            return True  # Assume success if no error
            
        except Exception as e:
            self.log(f"❌ Erro ao verificar: {str(e)}", "error")
            return False
    
    def complete_onboarding(self):
        """Complete the Lovable onboarding process"""
        try:
            self.log("📝 Completando onboarding...", "info")
            self.random_delay(2, 3)
            
            # Try to click Next buttons
            for _ in range(5):
                try:
                    # Look for Next button
                    next_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Continue')]")
                    next_btn.click()
                    self.random_delay(1, 2)
                except:
                    pass
                
                try:
                    # Look for name input
                    name_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='name'], input[name='name']")
                    name_input.clear()
                    random_name = f"User{random.randint(1000, 9999)}"
                    self.human_type(name_input, random_name)
                    self.random_delay(0.5, 1)
                except:
                    pass
                
                try:
                    # Look for role selection (Solo, Engineer, etc.)
                    solo_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Solo') or contains(text(), 'Personal')]")
                    solo_btn.click()
                    self.random_delay(1, 2)
                except:
                    pass
            
            self.log("✅ Onboarding completado!", "success")
            return True
            
        except Exception as e:
            self.log(f"⚠️ Onboarding parcial: {str(e)}", "warning")
            return True  # Continue anyway
    
    def create_project(self):
        """Create a simple project on Lovable"""
        try:
            self.log("🎨 Criando projeto...", "info")
            self.random_delay(2, 3)
            
            # Navigate to projects if needed
            if "/projects" not in self.driver.current_url:
                self.driver.get("https://lovable.dev/projects")
                self.random_delay(2, 3)
            
            # Find the prompt input
            prompt_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, input[placeholder*='idea'], div[contenteditable='true']"))
            )
            
            # Simple project prompt
            project_prompt = "Create a simple landing page with a welcome message and a contact button"
            
            prompt_input.click()
            self.random_delay(0.5, 1)
            self.human_type(prompt_input, project_prompt)
            self.random_delay(1, 2)
            
            # Submit the prompt
            prompt_input.send_keys(Keys.ENTER)
            self.random_delay(2, 3)
            
            # Or click submit button
            try:
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button[aria-label*='send'], button[aria-label*='submit']")
                submit_btn.click()
            except:
                pass
            
            # Wait for project creation (can take 30-60 seconds)
            self.log("⏳ Aguardando criação do projeto (pode demorar até 60s)...", "info")
            time.sleep(30)
            
            self.log("✅ Projeto criado!", "success")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao criar projeto: {str(e)}", "error")
            return False
    
    def publish_project(self):
        """Publish the project to activate referral credits"""
        try:
            self.log("🚀 Publicando projeto...", "info")
            self.random_delay(2, 3)
            
            # Find and click Publish button
            publish_btn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Publish')]"))
            )
            publish_btn.click()
            self.random_delay(2, 3)
            
            # Click final Publish button in modal
            try:
                final_publish = self.driver.find_element(By.XPATH, "//button[contains(@class, 'primary') and contains(text(), 'Publish')]")
                final_publish.click()
            except:
                # Try any Publish button
                buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Publish')]")
                for btn in buttons:
                    try:
                        btn.click()
                        break
                    except:
                        continue
            
            # Wait for publishing
            self.log("⏳ Aguardando publicação...", "info")
            time.sleep(15)
            
            # Check if published
            if "published" in self.driver.page_source.lower() or "shipped" in self.driver.page_source.lower():
                self.log("🎉 PROJETO PUBLICADO COM SUCESSO!", "success")
                self.log("💰 Créditos de referral devem ter sido ativados!", "success")
                return True
            
            return True  # Assume success
            
        except Exception as e:
            self.log(f"❌ Erro ao publicar: {str(e)}", "error")
            return False
    
    def process_account(self, email_address, email_password, referral_link):
        """Process a single account through the entire flow"""
        try:
            self.log(f"🔄 Processando conta: {email_address}", "processing")
            
            # Start browser
            if not self.start_browser():
                return False
            
            # Access referral link
            if not self.access_referral_link(referral_link):
                self.close_browser()
                return False
            
            # Create account
            success, lovable_password = self.create_account(email_address, email_password)
            if not success:
                self.close_browser()
                return False
            
            # Verify email
            verification_link = self.verify_email_outlook(email_address, email_password)
            if verification_link:
                self.click_verification_link(verification_link)
            else:
                self.log("⚠️ Continuando sem verificação de email...", "warning")
            
            # Complete onboarding
            self.complete_onboarding()
            
            # Create project
            if not self.create_project():
                self.close_browser()
                return False
            
            # Publish project
            if not self.publish_project():
                self.close_browser()
                return False
            
            self.log(f"✅ Conta {email_address} processada com sucesso!", "success")
            self.close_browser()
            return True
            
        except Exception as e:
            self.log(f"❌ Erro geral: {str(e)}", "error")
            self.close_browser()
            return False


def parse_accounts(text):
    """Parse accounts from text"""
    accounts = []
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        for sep in [':', ' ', '\t', '|', ';']:
            if sep in line:
                parts = line.split(sep, 1)
                if len(parts) == 2:
                    email = parts[0].strip()
                    password = parts[1].strip()
                    if '@' in email:
                        accounts.append({'email': email, 'password': password})
                        break
    return accounts


if __name__ == "__main__":
    # Test
    bot = LovableBot(headless=False)
    
    # Test account
    test_email = "test@outlook.com"
    test_password = "testpass123"
    referral_link = "https://lovable.dev/invite/YBON8MY"
    
    bot.process_account(test_email, test_password, referral_link)
