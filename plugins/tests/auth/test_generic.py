'''
test_generic.py

Copyright 2012 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
from nose.plugins.skip import SkipTest

from ..helper import PluginTest, PluginConfig
from core.data.parsers.urlParser import url_object
from core.data.url.xUrllib import xUrllib


class TestGeneric(PluginTest):
    
    base_url = 'http://moth/w3af/auth/generic/'
    demo_testfire = 'http://demo.testfire.net/bank/'
    
    _run_config = {
            'target': base_url,
            'plugins': {
                'discovery': (
                    PluginConfig('web_spider',
                                 ('onlyForward', True, PluginConfig.BOOL),
                                 ('ignoreRegex', '.*logout.*', PluginConfig.STR)),
                              
                ),
                'audit': (PluginConfig('xss',),),
                'auth':  (PluginConfig('generic',
                                 ('username', 'admin', PluginConfig.STR),
                                 ('password', 'admin', PluginConfig.STR),
                                 ('username_field', 'username', PluginConfig.STR),
                                 ('password_field', 'password', PluginConfig.STR),
                                 ('auth_url', url_object(base_url + 'auth.php') , PluginConfig.URL),
                                 ('check_url', url_object(base_url + 'home.php') , PluginConfig.URL),
                                 ('check_string', '<title>Home page</title>', PluginConfig.STR),
                            ),
                         ),
             }
        }
    
    demo_testfire_net = {
            'target': demo_testfire,
            'plugins': {
                'discovery': (
                    PluginConfig('web_spider',
                                 ('onlyForward', True, PluginConfig.BOOL),
                                 ('ignoreRegex', '.*logout.*', PluginConfig.STR),
                                 ('followRegex', '.*queryxpath.*', PluginConfig.STR)),
                              
                ),
                'auth':  (PluginConfig('generic',
                                 ('username', 'admin', PluginConfig.STR),
                                 ('password', 'admin', PluginConfig.STR),
                                 ('username_field', 'uid', PluginConfig.STR),
                                 ('password_field', 'passw', PluginConfig.STR),
                                 ('auth_url', url_object(demo_testfire + 'login.aspx') , PluginConfig.URL),
                                 ('check_url', url_object(demo_testfire + 'main.aspx') , PluginConfig.URL),
                                 ('check_string', 'View Recent Transactions', PluginConfig.STR),
                            ),
                         ),
             }
        }
    
    
    
    def test_post_auth_xss(self):
        self._scan(self._run_config['target'], self._run_config['plugins'])

        vulns = self.kb.getData('xss', 'xss')
        
        self.assertEquals( len(vulns), 1, vulns)
        
        vuln = vulns[0]
        self.assertEquals( vuln.getName(), 'Cross site scripting vulnerability', vuln.getName() )
        self.assertEquals( vuln.getVar(), 'section', vuln.getVar() )
        
    def test_demo_testfire_net(self):
        # We don't control the demo.testfire.net domain, so we'll check if its
        # up before doing anything else
        uri_opener = xUrllib()
        login_url = url_object(self.demo_testfire + 'login.aspx')
        try:
            res = uri_opener.GET(login_url)
        except:
            raise SkipTest('demo.testfire.net is unreachable!')
        else:
            if not 'Online Banking Login' in res.body: 
                raise SkipTest('demo.testfire.net has changed!')
    
        self._scan(self.demo_testfire_net['target'], self.demo_testfire_net['plugins'])

        urls = self.kb.getData('urls', 'url_objects')
        url_strings = set(str(u) for u in urls)
        
        self.assertTrue( self.demo_testfire + 'queryxpath.aspx' in url_strings ) 
        self.assertTrue( self.demo_testfire + 'queryxpath.aspx.cs' in url_strings )
        