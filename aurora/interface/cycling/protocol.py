# -*- coding: utf-8 -*-

from aurora.schemas.cycling import ElectroChemPayloads

class ProtocolList(list):
    def __setitem__(self, key, value):
        if not isinstance(value, ElectroChemPayloads.__args__):
            raise ValueError("Invalid technique")
        super().__setitem__(key, value)

    def add(self, elem):
        if not isinstance(elem, ElectroChemPayloads.__args__):
            raise ValueError("Invalid technique")
        super().append(elem)
    
    def remove(self, index):
        super().pop(index)
    
    def move_up(self, index):
        if index > 0:
            self[index-1], self[index] = self[index], self[index-1]
            return True
        else:
            return False

    def move_down(self, index):
        if index < len(self) - 1:
            self[index], self[index+1] = self[index+1], self[index]
            return True
        else:
            return False