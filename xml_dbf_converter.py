#!/usr/bin/env python
#-*- coding: cp1251 -*-

"""
Конвертирует XML в DBF и наоборот.
Скрипт принимает желаемый способ конвертации,
входное имя файла и желаемое выходное имя файла.
Затем парсит данные из входного файла, создает
выходной файл и записывает в него полученные данные.
Python 2.7.12
"""

from lxml import etree
from dbfpy import dbf
import sys
import codecs

def check_file_extension(filename, ext):
    """
    Проверяет указанное расширение и если
    оно не совпадает, выводит справку и
    прерывает выполнение скрипта.
    """
    if not filename.lower().endswith("." + ext):
        print_help()
        sys.exit(1)

def print_err(err = "Произошла ошибка!"):
    """
    Выводит ошибку и прерывает выполнение
    скрипта.
    """
    print("[Ошибка] {}".format(err))
    #print_help()
    sys.exit(1)

def print_chars_and_lines_count(filename):
    """
    Выводит общее кол-во символов и строк
    в файле.
    """
    chars = lines = 0
    with open(filename, "r") as f:
        for line in f:
            chars += len(line)
            lines += 1

    print "\nchars: {}, lines: {}".format(chars, lines)

def print_help():
    """
    Выводит описание аргументов и примеры
    использования скрипта.
    """
    print("\nПервый параметр: способ конвертации xml2dbf или dbf2xml"
          "\nВторой параметр: входное имя файла формата XML или DBF"
          "\nТретий параметр (необязателен): выходное название файла формата DBF или XML"
          "\nПример 1: "
          "python "+ sys.argv[0] +" xml2dbf database.xml"
          "\nПример 2: "
          "python "+ sys.argv[0] +" dbf2xml database.dbf database.xml")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if len(sys.argv) >= 3:
            if sys.argv[1] == 'xml2dbf':
                check_file_extension(sys.argv[2], "xml")

                if len(sys.argv) == 4:
                    check_file_extension(sys.argv[3], "dbf")
                    filename = sys.argv[3]
                else:
                    filename = sys.argv[2].rsplit(".",1)[0] + ".dbf"

                print("\nВходной файл: {}".format(sys.argv[2]))
                print("Выходной файл: {}".format(filename))

                try:
                    tree = etree.parse(sys.argv[2])
                except:
                    print_err()

                root = tree.getroot()

                FIELD_NAMES = [i.tag for i in list(root[0])]
                SCHEMA = tuple([(i.tag, "C", 235) for i in list(root[0])])

                db = dbf.Dbf(filename, new=True)

                db.addField(*SCHEMA)

                for element in root:
                    fields = dict([(i.tag, i.text) for i in element])
                    rec = db.newRecord()
                    for name in FIELD_NAMES:
                        rec[name] = fields[name].encode("cp866")
                    rec.store()

                db.close()

                print_chars_and_lines_count(filename)
                print("Готово!")

            elif sys.argv[1] == 'dbf2xml':
                check_file_extension(sys.argv[2], "dbf")

                if len(sys.argv) == 4:
                    check_file_extension(sys.argv[3], "xml")
                    filename = sys.argv[3]
                else:
                    filename = sys.argv[2].rsplit(".", 1)[0] + ".xml"

                print("\nВходной файл: {}".format(sys.argv[2]))
                print("Выходной файл: {}".format(filename))

                try:
                    db = dbf.Dbf(sys.argv[2])
                except:
                    print_err()

                FIELD_NAMES = db.fieldNames

                root = etree.Element("ROOT")

                for rec in db:
                    node = etree.SubElement(root, "NODE")
                    for name in FIELD_NAMES:
                        subelement = etree.SubElement(node, name)
                        subelement.text = rec[name]

                doc = etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)

                with codecs.open(filename, "w", "utf-8-sig") as f:
                    f.write(doc)

                print_chars_and_lines_count(filename)
                print("Готово!")

            else:
                print_help()
    else:
        print_help()