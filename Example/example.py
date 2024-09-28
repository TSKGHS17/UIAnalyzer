from PageCognition import PageCognition
from Driver import Driver

# 1. 获取截图和XML
driver = Driver()
img_path = "./screenshot.png"
xml_path = "./dom_tree.xml"

driver.screenshot(img_path)
driver.get_xml(xml_path)

# 2. 绘制SoM (可以直接传入路径)
SoM_path, UI_elements = PageCognition.draw_SoM(img_path, xml_path, driver)
print(UI_elements)

# 3. 绘制网格
grid_path, grids = PageCognition.grid(img_path)
print(grids)
