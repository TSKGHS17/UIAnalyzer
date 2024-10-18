from PageCognition import PageCognition
from Driver import Driver

# 1. 获取截图和XML
driver = Driver()
img_path = "./screenshot.png"
xml_path = "./dom_tree.xml"

driver.screenshot(img_path)
driver.get_xml(xml_path)

print(driver.get_activity())

# 2. 绘制SoM (可以直接传入已有图片和XML的路径，也可以不传入，会自动获取)
SoM_path, UI_elements = PageCognition.draw_SoM(img_path, xml_path)
for UI_element in UI_elements.items():
    print(UI_element)

# 3. 绘制网格
grid_path, grids = PageCognition.grid(img_path)
