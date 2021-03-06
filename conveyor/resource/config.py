import re
import os
from conveyor.event_manager.events import SpriteSheetPreloadEvent, MapPreloadEvent, TickEvent, ResourcesLoadedEvent, QuitEvent
from conveyor.gui import MapFactory, SpriteSheetFactory

def _intersperse(lst, item):
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result

class ConfigurationController(object):
    def __init__(self, event_manager, data_path):
        self._event_manager = event_manager
        self._event_manager.register_listener(self, [TickEvent, QuitEvent])
        self._map_factory = MapFactory(self._event_manager)
        self._sprite_sheet_factory = SpriteSheetFactory(self._event_manager)

        self._paths = dict()
        self._paths['{DATA_PATH}'] = data_path
        self._paths['{IMAGES}'] = 'images'
        self._paths['{MAPS}'] = 'maps'

    def notify(self, event):
        if isinstance(event, TickEvent):
            self._event_manager.unregister_listener(self, [TickEvent, QuitEvent])
            self._process_config_file()
            self._event_manager.post(ResourcesLoadedEvent())
            
        elif isinstance(event, QuitEvent):
            self._event_manager.unregister_listener(self)
            

    def _process_config_file(self):
        ''' Process the config file and fire off events to generate proper structures.
        '''
        config_file = open(os.path.join(self._paths['{DATA_PATH}'], 'config.ini'))

        try:
            NewEvent = None
            properties = dict()
            for ln in config_file:
                line = ln.strip()
                if line == '[SPRITES]':
                    NewEvent = SpriteSheetPreloadEvent
                elif line == '[MAPS]':
                    NewEvent = MapPreloadEvent
                elif line == 'END':
                    pass
                elif line == '':
                    if len(properties) != 0:
                        self._event_manager.post(NewEvent(properties))
                    properties = dict()
                    NewEvent = None
                else:
                    key,value = line.split(':', 1)

                    value_split = re.split('(%s)'%('|'.join(self._paths.keys())), value)
                    for i in range(len(value_split)):
                        if self._paths.has_key(value_split[i]):
                            value_split[i] = self._paths[value_split[i]]
      
                    if len(value_split) > 1:
                        value = os.path.join(*value_split)
                    
                    properties[key] = value
        except:
            raise
        finally:
            config_file.close()
