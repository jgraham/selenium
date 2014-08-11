# Copyright 2008-2013 Software freedom conservancy
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


try:
    import http.client as http_client
except ImportError:
    import httplib as http_client

import shutil
import socket
import sys
from .firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.extension_connection import ExtensionConnection
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.command import Command
from selenium.webdriver.common import utils
from selenium.webdriver.common.by import By

from marionette_transport.transport import MarionetteTransport


class WebDriver(RemoteWebDriver):

    # There is no native event support on Mac
    NATIVE_EVENTS_ALLOWED = sys.platform != "darwin"

    def __init__(self, firefox_profile=None, firefox_binary=None, timeout=30,
                 capabilities=None, proxy=None):
        self.session_id = None

        self.binary = firefox_binary
        self.profile = firefox_profile

        if self.profile is None:
            self.profile = FirefoxProfile()

        self.profile.native_events_enabled = (
            self.NATIVE_EVENTS_ALLOWED and self.profile.native_events_enabled)

        if self.binary is None:
            self.binary = FirefoxBinary()

        PORT = 2828  #utils.free_port()
        self.profile.port = PORT
        self.profile.update_preferences()

        self.binary.launch_browser(self.profile)

        if capabilities is None:
            capabilities = DesiredCapabilities.FIREFOX

        if proxy is not None:
            proxy.add_to_capabilities(capabilities)

        self.transport = MarionetteTransport('127.0.0.1', 2828)
        self.transport.connect()

        self.session_id = self._execute(Command.NEW_SESSION)['from']

        self._is_remote = False

    def quit(self):
        """Quits the driver and close every associated window."""
        try:
            self._execute("deleteSession")
        except (socket.error):
            # Happens if Firefox shutsdown before we've read the response from
            # the socket.
            pass
        self.binary.kill()
        try:
            shutil.rmtree(self.profile.path)
            if self.profile.tempfolder is not None:
                shutil.rmtree(self.profile.tempfolder)
        except Exception as e:
            print(str(e))

    def _execute(self, command, params=None):
        if not self.session_id and command != Command.NEW_SESSION:
            raise Exception("you need a sess dude!")

        message = {"name": command}

        if self.session_id:
            message["sessionId"] = self.session_id
        if params:
            message["parameters"] = params

        return self.transport.send(message)

    @property
    def firefox_profile(self):
        return self.profile

    def get(self, url):
        """
        Loads a web page in the current browser session.
        """
        self._execute(Command.GET, {'url': url})

    @property
    def title(self):
        """Returns the title of the current page.

        :Usage:
            driver.title
        """
        resp = self._execute(Command.GET_TITLE)
        return resp['value'] if resp['value'] is not None else ""

    def find_element_by_id(self, id_):
        """Finds an element by id.

        :Args:
         - id\_ - The id of the element to be found.

        :Usage:
            driver.find_element_by_id('foo')
        """
        return self.find_element(by=By.ID, value=id_)

    def find_elements_by_id(self, id_):
        """
        Finds multiple elements by id.

        :Args:
         - id\_ - The id of the elements to be found.

        :Usage:
            driver.find_element_by_id('foo')
        """
        return self.find_elements(by=By.ID, value=id_)

    def find_element_by_xpath(self, xpath):
        """
        Finds an element by xpath.

        :Args:
         - xpath - The xpath locator of the element to find.

        :Usage:
            driver.find_element_by_xpath('//div/td[1]')
        """
        return self.find_element(by=By.XPATH, value=xpath)

    def find_elements_by_xpath(self, xpath):
        """
        Finds multiple elements by xpath.

        :Args:
         - xpath - The xpath locator of the elements to be found.

        :Usage:
            driver.find_elements_by_xpath("//div[contains(@class, 'foo')]")
        """
        return self.find_elements(by=By.XPATH, value=xpath)

    def find_element_by_link_text(self, link_text):
        """
        Finds an element by link text.

        :Args:
         - link_text: The text of the element to be found.

        :Usage:
            driver.find_element_by_link_text('Sign In')
        """
        return self.find_element(by=By.LINK_TEXT, value=link_text)

    def find_elements_by_link_text(self, text):
        """
        Finds elements by link text.

        :Args:
         - link_text: The text of the elements to be found.

        :Usage:
            driver.find_elements_by_link_text('Sign In')
        """
        return self.find_elements(by=By.LINK_TEXT, value=text)

    def find_element_by_partial_link_text(self, link_text):
        """
        Finds an element by a partial match of its link text.

        :Args:
         - link_text: The text of the element to partially match on.

        :Usage:
            driver.find_element_by_partial_link_text('Sign')
        """
        return self.find_element(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_elements_by_partial_link_text(self, link_text):
        """
        Finds elements by a partial match of their link text.

        :Args:
         - link_text: The text of the element to partial match on.

        :Usage:
            driver.find_element_by_partial_link_text('Sign')
        """
        return self.find_elements(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_element_by_name(self, name):
        """
        Finds an element by name.

        :Args:
         - name: The name of the element to find.

        :Usage:
            driver.find_element_by_name('foo')
        """
        return self.find_element(by=By.NAME, value=name)

    def find_elements_by_name(self, name):
        """
        Finds elements by name.

        :Args:
         - name: The name of the elements to find.

        :Usage:
            driver.find_elements_by_name('foo')
        """
        return self.find_elements(by=By.NAME, value=name)

    def find_element_by_tag_name(self, name):
        """
        Finds an element by tag name.

        :Args:
         - name: The tag name of the element to find.

        :Usage:
            driver.find_element_by_tag_name('foo')
        """
        return self.find_element(by=By.TAG_NAME, value=name)

    def find_elements_by_tag_name(self, name):
        """
        Finds elements by tag name.

        :Args:
         - name: The tag name the use when finding elements.

        :Usage:
            driver.find_elements_by_tag_name('foo')
        """
        return self.find_elements(by=By.TAG_NAME, value=name)

    def find_element_by_class_name(self, name):
        """
        Finds an element by class name.

        :Args:
         - name: The class name of the element to find.

        :Usage:
            driver.find_element_by_class_name('foo')
        """
        return self.find_element(by=By.CLASS_NAME, value=name)

    def find_elements_by_class_name(self, name):
        """
        Finds elements by class name.

        :Args:
         - name: The class name of the elements to find.

        :Usage:
            driver.find_elements_by_class_name('foo')
        """
        return self.find_elements(by=By.CLASS_NAME, value=name)

    def find_element_by_css_selector(self, css_selector):
        """
        Finds an element by css selector.

        :Args:
         - css_selector: The css selector to use when finding elements.

        :Usage:
            driver.find_element_by_css_selector('#foo')
        """
        return self.find_element(by=By.CSS_SELECTOR, value=css_selector)

    def find_elements_by_css_selector(self, css_selector):
        """
        Finds elements by css selector.

        :Args:
         - css_selector: The css selector to use when finding elements.

        :Usage:
            driver.find_elements_by_css_selector('.foo')
        """
        return self.find_elements(by=By.CSS_SELECTOR, value=css_selector)

    def execute_script(self, script, *args):
        """
        Synchronously Executes JavaScript in the current window/frame.

        :Args:
         - script: The JavaScript to execute.
         - \*args: Any applicable arguments for your JavaScript.

        :Usage:
            driver.execute_script('document.title')
        """
        converted_args = list(args)
        return self._execute(Command.EXECUTE_SCRIPT,
            {'script': script, 'args':converted_args})['value']

    def execute_async_script(self, script, *args):
        """
        Asynchronously Executes JavaScript in the current window/frame.

        :Args:
         - script: The JavaScript to execute.
         - \*args: Any applicable arguments for your JavaScript.

        :Usage:
            driver.execute_async_script('document.title')
        """
        converted_args = list(args)
        return self._execute(Command.EXECUTE_ASYNC_SCRIPT,
            {'script': script, 'args':converted_args})['value']

    @property
    def current_url(self):
        """
        Gets the URL of the current page.

        :Usage:
            driver.current_url
        """
        return self._execute(Command.GET_CURRENT_URL)['value']

    @property
    def page_source(self):
        """
        Gets the source of the current page.

        :Usage:
            driver.page_source
        """
        return self._execute(Command.GET_PAGE_SOURCE)['value']

    def close(self):
        """
        Closes the current window.

        :Usage:
            driver.close()
        """
        self._execute(Command.CLOSE)

    def quit(self):
        """
        Quits the driver and closes every associated window.

        :Usage:
            driver.quit()
        """
        try:
            self._execute("deleteSession")
        finally:
            self.stop_client()

    @property
    def current_window_handle(self):
        """
        Returns the handle of the current window.

        :Usage:
            driver.current_window_handle
        """
        return self._execute(Command.GET_CURRENT_WINDOW_HANDLE)['value']

    @property
    def window_handles(self):
        """
        Returns the handles of all windows within the current session.

        :Usage:
            driver.window_handles
        """
        return self._execute(Command.GET_WINDOW_HANDLES)['value']

    def maximize_window(self):
        """
        Maximizes the current window that webdriver is using
        """
        self._execute(Command.MAXIMIZE_WINDOW, {"windowHandle": "current"})

    @property
    def switch_to(self):
        return self._switch_to

    #Target Locators
    def switch_to_active_element(self):
        """ Deprecated use driver.switch_to.active_element
        """
        warnings.warn("use driver.switch_to.active_element instead", DeprecationWarning)
        return self._switch_to.active_element

    def switch_to_window(self, window_name):
        """ Deprecated use driver.switch_to.window
        """
        warnings.warn("use driver.switch_to.window instead", DeprecationWarning)
        self._switch_to.window(window_name)

    def switch_to_frame(self, frame_reference):
        """ Deprecated use driver.switch_to.frame
        """
        warnings.warn("use driver.switch_to.frame instead", DeprecationWarning)
        self._switch_to.frame(frame_reference)

    def switch_to_default_content(self):
        """ Deprecated use driver.switch_to.default_content
        """
        warnings.warn("use driver.switch_to.default_content instead", DeprecationWarning)
        self._switch_to.default_content()

    def switch_to_alert(self):
        """ Deprecated use driver.switch_to.alert
        """
        warnings.warn("use driver.switch_to.alert instead", DeprecationWarning)
        return self._switch_to.alert

    #Navigation
    def back(self):
        """
        Goes one step backward in the browser history.

        :Usage:
            driver.back()
        """
        self._execute(Command.GO_BACK)

    def forward(self):
        """
        Goes one step forward in the browser history.

        :Usage:
            driver.forward()
        """
        self._execute(Command.GO_FORWARD)

    def refresh(self):
        """
        Refreshes the current page.

        :Usage:
            driver.refresh()
        """
        self._execute(Command.REFRESH)

    # Options
    def get_cookies(self):
        """
        Returns a set of dictionaries, corresponding to cookies visible in the current session.

        :Usage:
            driver.get_cookies()
        """
        return self._execute(Command.GET_ALL_COOKIES)['value']

    def get_cookie(self, name):
        """
        Get a single cookie by name. Returns the cookie if found, None if not.

        :Usage:
            driver.get_cookie('my_cookie')
        """
        cookies = self.get_cookies()
        for cookie in cookies:
            if cookie['name'] == name:
                return cookie
        return None

    def delete_cookie(self, name):
        """
        Deletes a single cookie with the given name.

        :Usage:
            driver.delete_cookie('my_cookie')
        """
        self._execute(Command.DELETE_COOKIE, {'name': name})

    def delete_all_cookies(self):
        """
        Delete all cookies in the scope of the session.

        :Usage:
            driver.delete_all_cookies()
        """
        self._execute(Command.DELETE_ALL_COOKIES)

    def add_cookie(self, cookie_dict):
        """
        Adds a cookie to your current session.

        :Args:
         - cookie_dict: A dictionary object, with required keys - "name" and "value";
            optional keys - "path", "domain", "secure", "expiry"

        Usage:
            driver.add_cookie({'name' : 'foo', 'value' : 'bar'})
            driver.add_cookie({'name' : 'foo', 'value' : 'bar', 'path' : '/'})
            driver.add_cookie({'name' : 'foo', 'value' : 'bar', 'path' : '/', 'secure':True})

        """
        self._execute(Command.ADD_COOKIE, {'cookie': cookie_dict})

    # Timeouts
    def implicitly_wait(self, time_to_wait):
        """
        Sets a sticky timeout to implicitly wait for an element to be found,
           or a command to complete. This method only needs to be called one
           time per session. To set the timeout for calls to
           execute_async_script, see set_script_timeout.

        :Args:
         - time_to_wait: Amount of time to wait (in seconds)

        :Usage:
            driver.implicitly_wait(30)
        """
        self._execute(Command.IMPLICIT_WAIT, {'ms': float(time_to_wait) * 1000})

    def set_script_timeout(self, time_to_wait):
        """
        Set the amount of time that the script should wait during an
           execute_async_script call before throwing an error.

        :Args:
         - time_to_wait: The amount of time to wait (in seconds)

        :Usage:
            driver.set_script_timeout(30)
        """
        self._execute(Command.SET_SCRIPT_TIMEOUT,
            {'ms': float(time_to_wait) * 1000})

    def set_page_load_timeout(self, time_to_wait):
        """
        Set the amount of time to wait for a page load to complete
           before throwing an error.

        :Args:
         - time_to_wait: The amount of time to wait

        :Usage:
            driver.set_page_load_timeout(30)
        """
        self._execute(Command.SET_TIMEOUTS,
            {'ms': float(time_to_wait) * 1000, 'type':'page load'})

    def find_element(self, by=By.ID, value=None):
        """
        'Private' method used by the find_element_by_* methods.

        :Usage:
            Use the corresponding find_element_by_* instead of this.

        :rtype: WebElement
        """
        if not By.is_valid(by) or not isinstance(value, str):
            raise InvalidSelectorException("Invalid locator values passed in")

        return self._execute(Command.FIND_ELEMENT,
                             {'using': by, 'value': value})['value']

    def find_elements(self, by=By.ID, value=None):
        """
        'Private' method used by the find_elements_by_* methods.

        :Usage:
            Use the corresponding find_elements_by_* instead of this.

        :rtype: list of WebElement
        """
        if not By.is_valid(by) or not isinstance(value, str):
            raise InvalidSelectorException("Invalid locator values passed in")

        return self._execute(Command.FIND_ELEMENTS,
                             {'using': by, 'value': value})['value']
    @property
    def desired_capabilities(self):
        """
        returns the drivers current desired capabilities being used
        """
        return self.capabilities

    def get_screenshot_as_file(self, filename):
        """
        Gets the screenshot of the current window. Returns False if there is
           any IOError, else returns True. Use full paths in your filename.

        :Args:
         - filename: The full path you wish to save your screenshot to.

        :Usage:
            driver.get_screenshot_as_file('/Screenshots/foo.png')
        """
        png = self.get_screenshot_as_png()
        try:
            with open(filename, 'wb') as f:
                f.write(png)
        except IOError:
            return False
        finally:
            del png
        return True

    save_screenshot = get_screenshot_as_file

    def get_screenshot_as_png(self):
        """
        Gets the screenshot of the current window as a binary data.

        :Usage:
            driver.get_screenshot_as_png()
        """
        return base64.b64decode(self.get_screenshot_as_base64().encode('ascii'))

    def get_screenshot_as_base64(self):
        """
        Gets the screenshot of the current window as a base64 encoded string
           which is useful in embedded images in HTML.

        :Usage:
            driver.get_screenshot_as_base64()
        """
        return self._execute(Command.SCREENSHOT)['value']

    def set_window_size(self, width, height, windowHandle='current'):
        """
        Sets the width and height of the current window. (window.resizeTo)

        :Args:
         - width: the width in pixels to set the window to
         - height: the height in pixels to set the window to

        :Usage:
            driver.set_window_size(800,600)
        """
        self._execute(Command.SET_WINDOW_SIZE, {'width': int(width), 'height': int(height),
          'windowHandle': windowHandle})

    def get_window_size(self, windowHandle='current'):
        """
        Gets the width and height of the current window.

        :Usage:
            driver.get_window_size()
        """
        return self._execute(Command.GET_WINDOW_SIZE,
            {'windowHandle': windowHandle})['value']

    def set_window_position(self, x, y, windowHandle='current'):
        """
        Sets the x,y position of the current window. (window.moveTo)

        :Args:
         - x: the x-coordinate in pixels to set the window position
         - y: the y-coordinate in pixels to set the window position

        :Usage:
            driver.set_window_position(0,0)
        """
        self._execute(Command.SET_WINDOW_POSITION, {'x': int(x), 'y': int(y),
          'windowHandle': windowHandle})

    def get_window_position(self, windowHandle='current'):
        """
        Gets the x,y position of the current window.

        :Usage:
            driver.get_window_position()
        """
        return self._execute(Command.GET_WINDOW_POSITION,
            {'windowHandle': windowHandle})['value']

    @property
    def orientation(self):
        """
        Gets the current orientation of the device

        :Usage:
            orientation = driver.orientation
        """
        return self._execute(Command.GET_SCREEN_ORIENTATION)['value']

    @orientation.setter
    def orientation(self, value):
        """
        Sets the current orientation of the device

        :Args:
         - value: orientation to set it to.

        :Usage:
            driver.orientation = 'landscape'
        """
        allowed_values = ['LANDSCAPE', 'PORTRAIT']
        if value.upper() in allowed_values:
            self._execute(Command.SET_SCREEN_ORIENTATION, {'orientation': value})
        else:
            raise WebDriverException("You can only set the orientation to 'LANDSCAPE' and 'PORTRAIT'")

    @property
    def application_cache(self):
        """ Returns a ApplicationCache Object to interact with the browser app cache"""
        return ApplicationCache(self)

    @property
    def log_types(self):
        """
        Gets a list of the available log types

        :Usage:
            driver.log_types
        """
        return self._execute(Command.GET_AVAILABLE_LOG_TYPES)['value']

    def get_log(self, log_type):
        """
        Gets the log for a given log type

        :Args:
         - log_type: type of log that which will be returned

        :Usage:
            driver.get_log('browser')
            driver.get_log('driver')
            driver.get_log('client')
            driver.get_log('server')
        """
        return self._execute(Command.GET_LOG, {'type': log_type})['value']