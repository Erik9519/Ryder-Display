import os
import sys
import math
import json
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QLabel

from UIModules.ForegroundProcess import ForegroundProcess
from UIModules.CornerProgressBar import CornerProgressBar
from UIModules.RoundProgressBar import RoundProgressBar
from UIModules.DynamicTextBool import DynamicTextBool
from UIModules.DynamicText import DynamicText
from UIModules.ProgressBar import ProgressBar
from UIModules.Graph import Graph

from Network.Client import Client
from Network.Server import Server

class HomeConfigurationParser(object):
    def parse(window, client : Client, server : Server, path: str):
        ui_dynamic = []
        ui_static = []
        file = open(path, 'r')
        config = json.loads(file.read())
        file.close()

        ts = math.ceil(config['fps'] / 2)
        pos = config['ui'][0]['pos'].copy()
        new_pos = config['ui'][0]['pos'].copy()
        for entry in config['ui']:
            is_dynamic = True
            elem = None
            update_pos = [True, True]
            # Pos X
            if isinstance(entry['pos'][0], str):
                if entry['pos'][0][0] != "d":
                    new_pos[0] = pos[0] + int(entry['pos'][0])
                else:
                    update_pos[0] = False
                    if len(entry['pos'][0]) > 1:
                        new_pos[0] = pos[0] + int(entry['pos'][0][1:])
            else:
                new_pos[0] = entry['pos'][0]
            # Pos Y
            if isinstance(entry['pos'][1], str):
                if entry['pos'][1][0] != "d":
                    new_pos[1] = pos[1] + int(entry['pos'][1])
                else:
                    update_pos[1] = False
                    if len(entry['pos'][1]) > 1:
                        new_pos[1] = pos[1] + int(entry['pos'][1][1:])
            else:
                new_pos[1] = entry['pos'][1]
            # Parse Element
            print(entry['title'] + ", " + str(new_pos[0]) + ", " + str(new_pos[1]))
            if entry['type'] == 'ForegroundProcessIcon':
                elem = ForegroundProcess(
                    window, client, server,
                    new_pos.copy(), entry['size'], path[0:path.rfind('/')]
                )
            elif entry['type'] == 'Graph':
                unit = entry['unit']
                if len(entry['unit']) > 0:
                    if entry['unit'][0] == '*':
                        unit = config['unit_converters'][entry['unit'][1:]]
                elem = Graph(
                    window, new_pos.copy(), entry['size'], entry['color'], entry['thickness'],
                    entry['max_text_length'], entry['stylesheet'], unit, entry['n_values'], entry['metric']
                )
            elif entry['type'] == 'RoundProgressBar':
                elem = RoundProgressBar(
                    window, ts,
                    new_pos.copy(), entry['size'], entry['angle'], entry['colors'], entry['thickness'],
                    entry['metric']['name'], entry['metric']['bounds']
                )
            elif entry['type'] == 'CornerProgressBar':
                elem = CornerProgressBar(
                    window, ts,
                    new_pos.copy(), entry['size'], entry['direction'], entry['colors'], entry['thickness'],
                    entry['cornerRadius'], entry['metric']['name'], entry['metric']['bounds']
                )
            elif entry['type'] == 'ProgressBar':
                elem = ProgressBar(
                    window, ts,
                    new_pos.copy(), entry['size'], entry['direction'], entry['stylesheet'],
                    entry['metric']['name'], entry['metric']['bounds']
                )
            elif entry['type'] == 'StaticText':
                elem = HomeConfigurationParser._createLabel(
                    window,
                    entry['stylesheet'],
                    entry['text']['msg'],
                    entry['text']['alignment'],
                    new_pos.copy()
                )
                is_dynamic = False
            elif entry['type'] == 'DynamicText':
                unit = entry['unit']
                if len(entry['unit']) > 0:
                    if entry['unit'][0] == '*':
                        unit = config['unit_converters'][entry['unit'][1:]]
                elem = DynamicText(
                    window,
                    entry['stylesheet'], entry['max_text_length'], unit, entry['alignment'], new_pos.copy(), entry['metric']
                )
            elif entry['type'] == 'DynamicTextBool':
                elem = DynamicTextBool(
                    window,
                    entry['stylesheet'], entry['text'], entry['alignment'], new_pos.copy(), entry['metric']
                )
            elif entry['type'] == 'Image':
                elem = HomeConfigurationParser._createImage(
                    window, entry['path'], new_pos.copy(), entry['size']
                )
                is_dynamic = False

            if update_pos[0]:
                pos[0] = new_pos[0]
            if update_pos[1]:
                pos[1] = new_pos[1]

            if is_dynamic:
                ui_dynamic.append(elem)
            else:
                ui_static.append(elem)

        return config['fps'], ui_dynamic

    def _createLabel(window, stylesheet, text, alignment, pos):
        label = QLabel(window)
        label.setText(text)
        label.setStyleSheet('QLabel{'+stylesheet+'}')
        label.setAttribute(Qt.WA_TranslucentBackground)
        label.adjustSize()
        if alignment == "left":
            label.setAlignment(Qt.AlignLeft)
            label.move(pos[0],pos[1])
        elif alignment == "center":
            label.setAlignment(Qt.AlignHCenter)
            label.move(pos[0] - label.width() / 2,pos[1])
        elif alignment == "right":
            label.setAlignment(Qt.AlignRight)
            label.move(pos[0] - label.width(),pos[1])
        label.show()
        return label

    def _createImage(window, image, pos, size):
        path = os.path.dirname(sys.argv[0])+'/Resources/'+image
        extension = path[(path.rfind('.')+1):]
        elem = None
        if extension == 'svg':
            elem = QSvgWidget(path, window)
            elem.setGeometry(pos[0], pos[1], size[0], size[1])
            elem.show()
        return elem
