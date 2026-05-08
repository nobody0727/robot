nonebot.init(
    driver = "^nonebot.plugin.onesbot",
    adaptive_port = true
)

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBot11Adapter

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(OneBot11Adapter)

nonebot.load_plugin("nonebot_plugin_apscheduler")

nonebot.run()
