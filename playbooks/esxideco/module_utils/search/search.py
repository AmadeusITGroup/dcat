import csv

class Search():
    def __init__(self):
        self.final_result ={}
        self.final_result['ccat1'] = {}

    def search_ccat1(self, category):
        with open('module_utils/search/changecat1.csv', mode='r') as ccat1:
            reader = csv.reader(ccat1)
            for line in list(reader):
                if category in line[3]:
                    if line[2] not in self.final_result['ccat1']:
                        self.final_result['ccat1'][line[2]] = {}
                        self.final_result['ccat1'][line[2]]['ccat2'] = {}
                        self.final_result['ccat1'][line[2]]['ccat3'] = {}
                    self.search_ccat2(line[0], line[2])

    def search_ccat2(self, id, value):
        with open('module_utils/search/changecat2.csv', mode='r') as ccat2:
            reader = csv.reader(ccat2)
            for line in list(reader):
                if id in line[5]:
                    if line[2] not in self.final_result['ccat1'][value]['ccat2']:
                        self.final_result['ccat1'][value]['ccat2'][line[2]] = {}
                        self.final_result['ccat1'][value]['ccat2'][line[2]]['ccat3'] = {}
                    self.search_ccat3(line[0], value, line[2])

    def search_ccat3(self, id, value, value1):
        with open('module_utils/search/changecat3.csv', mode='r', encoding='windows-1252') as ccat3:
            reader = csv.reader(ccat3)
            for line in list(reader):
                if id in line[5]:
                    if line[2] not in self.final_result['ccat1'][value]['ccat2'][value1]['ccat3']:
                        self.final_result['ccat1'][value]['ccat2'][value1]['ccat3'] = line[2]

    def get_final_result(self):
        return self.final_result

