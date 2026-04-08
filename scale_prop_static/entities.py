from dataclasses import dataclass

ENTITY_DEFINE_START = "entity\n{"
ENTITY_DEFINE_END = "	}\n}"

@dataclass
class VMF:
    """Valve Map Format (VMF) file to manipulate"""

    string: str
    path: str

    def GetValueFromKey(self, instance: str, key: str) -> str:
        if key not in instance:
            return KeyError

        key_storage = f'"{key}" "'
        key_start = instance.find(key_storage)

        if key_start == -1:
            return KeyError
        
        return instance[key_start + len(key_storage):instance.find('"\n', key_start)]

    def GetEntities(self) -> list[str]:
        start_index = 0
        indices: list[int] = []

        while True:
            pos = self.string.find(ENTITY_DEFINE_START, start_index)

            if pos == -1:
                break

            indices.append(pos)

            # Start searching from after the found instance
            start_index = pos + 1

        entities: list[str] = []

        for index, pos in enumerate(indices):
            try:
                search_end = indices[index + 1]
            except IndexError:
                search_end = None

            entity_end = self.string.find(ENTITY_DEFINE_END, pos, search_end)
            entity_instance = self.string[pos:entity_end + len(ENTITY_DEFINE_END)]
            entities.append(entity_instance)

        return entities

@dataclass
class PropStatic(slots = True):
    """`prop_static` instance and it's info."""

    instance: str
    id: int
    model: str
    uniformscale: float

HIGH_PRIORITY_VALUES = set([
    "scale"
])

@dataclass
class QC(slots = True):
    """QC file (model compile script) to manipulate"""

    string: str
    path: str

    def GetValueFromKey(self, key: str) -> str:
        key_index = self.string.find(f"${key}")

        if key_index == -1:
            raise KeyError

        key_end_index = self.string.find(" ", key_index)
        value_end_index = self.string.find("\n$", key_end_index)
        value = self.string[key_end_index + 1:value_end_index - 1].replace('"', "")

        return value

    def SetValue(self, key: str, value: str):
        key_index = self.string.find(f"${key}")

        if key_index != -1:
            key_end_index = self.string.find(" ", key_index)
            value_end_index = self.string.find("\n$", key_end_index)
            self.string = self.string[:key_end_index + 1] + value + self.string[value_end_index - 1:]
        else:
            if HIGH_PRIORITY_VALUES:
                line_after_model = self.string.find("\n", self.string.find("$modelname"))
                self.string = self.string[:line_after_model] + f"\n\n${key} {value}" + self.string[line_after_model:]
            else:
                self.string = self.string + f"\n${key} {value}"

    def DeleteKey(self, key: str):
        key_index = self.string.find(f"${key}")

        if key_index == -1:
            raise KeyError

        key_end_index = self.string.find(" ", key_index)
        value_end_index = self.string.find("\n$", key_end_index)
        self.string = self.string[:key_index] + self.string[value_end_index:]