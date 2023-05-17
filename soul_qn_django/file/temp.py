from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import *
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


# 绘制饼状图
def DrawPie():
    d = Drawing(400, 400)

    d.add(String(0, 160, "2021年销量饼图",
                 fontSize=16, fontName='微软雅黑',
                 fillColor=colors.black))
    pc = Pie()
    pc.x = 200
    pc.y = 0
    pc.data = [10, 10, 40, 10, 20, 10, 10, 10]

    pc.labels = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月']
    pc.slices.fontName = '微软雅黑'
    pc.slices.strokeWidth = 0.5
    pc.slices[3].popout = 5
    pc.slices[3].strokeWidth = 1
    pc.slices[3].strokeDashArray = [1, 1]
    # pc.slices[3].labelRadius = 1.75
    pc.slices[3].fontColor = colors.red
    d.add(pc)

    return d


# 绘制柱状图
def drawBarChart():
    drawing = Drawing(400, 250)
    drawing.add(String(50, 180, "2021年销量柱状图", fontSize=16, fontName='微软雅黑', fillColor=colors.black))

    drawing.add(Rect(320, 240, 5, 5, fillColor=colors.gray, strokeColor=colors.white))
    drawing.add(String(326, 240, "张三", fontSize=5, fontName='微软雅黑', fillColor=colors.gray))
    drawing.add(Rect(340, 240, 5, 5, fillColor=colors.green, strokeColor=colors.white))
    drawing.add(String(346, 240, "李四", fontSize=5, fontName='微软雅黑', fillColor=colors.green))
    drawing.add(Rect(360, 240, 5, 5, fillColor=colors.green, strokeColor=colors.white))
    drawing.add(String(366, 240, "王五", fontSize=5, fontName='微软雅黑', fillColor=colors.blue))
    drawing.add(Rect(380, 240, 5, 5, fillColor=colors.red, strokeColor=colors.white))
    drawing.add(String(386, 240, "赵六", fontSize=5, fontName='微软雅黑', fillColor=colors.red))

    data = [
        (13, 5, 20, 22, 37, 45, 19, 4),
        (14, 6, 21, 23, 38, 46, 20, 5),
        (14, 6, 21, 23, 38, 46, 20, 5),
        (14, 6, 21, 23, 38, 46, 20, 7)
    ]
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = data
    bc.strokeColor = colors.gray
    bc.bars[0].fillColor = colors.gray
    bc.bars[1].fillColor = colors.green
    bc.bars[2].fillColor = colors.blue
    bc.bars[3].fillColor = colors.red
    bc.groupSpacing = 2  # 每组柱状图之间的间隔
    bc.barSpacing = 1  # 每个柱状图之间的间隔
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 50
    bc.valueAxis.valueStep = 10
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.labels.setProperties({"fontName": "微软雅黑"})
    bc.categoryAxis.categoryNames = ['1月', '2月', '3月',
                                     '4月', '5月', '6月', '7月', '8月']
    drawing.add(bc)
    return drawing


# 绘制线性图
def drawLineChart():
    drawing = Drawing(400, 250)
    drawing.add(String(50, 230, "2021销量线形图", fontSize=16, fontName='微软雅黑', fillColor=colors.black))

    drawing.add(Rect(350, 240, 5, 5, fillColor=colors.green, strokeColor=colors.white))
    drawing.add(String(356, 240, "张三", fontSize=5, fontName='微软雅黑', fillColor=colors.green))

    drawing.add(Rect(370, 240, 5, 5, fillColor=colors.red, strokeColor=colors.white))
    drawing.add(String(376, 240, "李四", fontSize=5, fontName='微软雅黑', fillColor=colors.red))

    data = [
        (13, 5, 20, 22, 37, 45, 19, 4),
        (5, 20, 46, 38, 23, 21, 6, 14)
    ]
    lc = HorizontalLineChart()
    lc.x = 50
    lc.y = 50
    lc.height = 125
    lc.width = 300
    lc.data = data
    lc.joinedLines = 1
    lc.categoryAxis.categoryNames = ['1月', '2月', '3月',
                                     '4月', '5月', '6月', '7月', '8月']
    lc.categoryAxis.labels.setProperties({"fontName": "微软雅黑"})
    lc.categoryAxis.labels.boxAnchor = 'n'
    lc.valueAxis.valueMin = 0
    lc.valueAxis.valueMax = 60
    lc.valueAxis.valueStep = 15
    lc.lines[0].strokeColor = colors.green
    lc.lines[1].strokeColor = colors.yellow
    lc.lines[0].strokeWidth = 2
    lc.lines[1].strokeWidth = 2
    drawing.add(lc)
    return drawing


# 绘制带标记的线性图
def drawLineChartwithMarker():
    drawing = Drawing(400, 250)
    drawing.add(String(50, 230, "2021销量线形图(标记每个点)", fontSize=16, fontName='微软雅黑', fillColor=colors.black))

    drawing.add(Rect(350, 240, 5, 5, fillColor=colors.green, strokeColor=colors.white))
    drawing.add(String(356, 240, "张三", fontSize=5, fontName='微软雅黑', fillColor=colors.green))

    drawing.add(Rect(370, 240, 5, 5, fillColor=colors.red, strokeColor=colors.white))
    drawing.add(String(376, 240, "李四", fontSize=5, fontName='微软雅黑', fillColor=colors.red))

    drawing.add(String(358, 47, "月份", fontSize=5, fontName='微软雅黑', fillColor=colors.black))
    drawing.add(String(45, 180, "销量", fontSize=5, fontName='微软雅黑', fillColor=colors.black))

    data = [
        ((1, 1), (2, 2), (3, 2.5), (4, 3), (5, 5)),
        ((1, 2), (2, 3), (3, 2.5), (4, 5), (5, 6))
    ]
    lp = LinePlot()
    lp.x = 50
    lp.y = 50
    lp.height = 125
    lp.width = 300
    lp.data = data
    lp.joinedLines = 1
    lp.lines[0].strokeColor = colors.green
    lp.lines[1].strokeColor = colors.red
    lp.lines[0].symbol = makeMarker('FilledCircle')
    lp.lines[1].symbol = makeMarker('Circle')
    lp.lineLabelFormat = '%2.0f'
    lp.strokeColor = colors.white
    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 5
    lp.xValueAxis.valueSteps = [1, 2, 3, 4, 5]
    lp.xValueAxis.labelTextFormat = '%2.1f'
    lp.yValueAxis.valueMin = 0
    lp.yValueAxis.valueMax = 7
    lp.yValueAxis.valueSteps = [1, 2, 3, 4, 5, 6]
    drawing.add(lp)
    return drawing


if __name__ == '__main__':
    pdfmetrics.registerFont(TTFont('微软雅黑', './fonts/font1716.ttf'))
    doc = SimpleDocTemplate("drawpic.pdf", pagesize=A4, leftMargin=10, rightMargin=0, topMargin=50, bottomMargin=30)
    contents = []
    contents.append(
        Paragraph("绘图研究", style=ParagraphStyle(name="test", fontName='微软雅黑', fontSize=20, alignment=TA_CENTER)))

    contents.append(Spacer(doc.width, 30))

    contents.append(DrawPie())

    contents.append(Spacer(doc.width, 30))

    contents.append(drawBarChart())
    contents.append(Spacer(doc.width, 30))
    contents.append(drawLineChart())
    contents.append(Spacer(doc.width, 30))
    contents.append(drawLineChartwithMarker())

    doc.build(contents)
