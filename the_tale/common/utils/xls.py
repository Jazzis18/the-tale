# coding: utf-8

import xlrd
import rels


class XLSException(Exception): pass


def load_table(filename, sheet_index=0, encoding='utf-8', rows=None, columns=None, data_type=lambda x: x): # pylint: disable=R0912,R0914,R0915

    if rows and len(set(rows)) != len(rows):
        raise XLSException('duplicate row id')

    if columns and len(set(columns)) != len(columns):
        raise XLSException('duplicate column id')

    book = xlrd.open_workbook(filename, logfile=None, encoding_override=encoding)

    sheet = book.sheet_by_index(sheet_index)

    visited = False

    row_rows = []

    for row_number in xrange(sheet.nrows):

        row_data = list(sheet.row_values(row_number))

        if not any(row_data):
            if visited: break
            else: continue

        row_rows.append(row_data)

    left_border_index = 0
    right_border_index = -1

    for row in row_rows:
        for i, element in enumerate(row):
            if element != '':
                left_border_index = i
                break

        for i, element in enumerate(row[left_border_index:], start=left_border_index):
            if element == '' and i > right_border_index:
                right_border_index = i
                break

        if right_border_index == -1: right_border_index = len(row)

    data = [row[left_border_index:right_border_index+1] for row in row_rows]

    if rows and columns:
        new_data = {}
        real_columns = data[0][1:]

        if set(real_columns) != set(columns):
            raise XLSException('wrong columns ids: %r' % (real_columns, ))

        for row in data[1:]:
            row_id = row[0]

            if row_id not in rows:
                raise XLSException('unknown row id: "%s"' % (row_id,))

            if row_id in new_data:
                raise XLSException('duplicate row id: "%s"' % (row_id, ))

            if len(row[1:]) != len(columns):
                raise XLSException('wrong number of elements in row: %r' % (row[1:], ))

            new_data[row_id] = dict(zip(real_columns, [ data_type(el) for el in row[1:]]))

        return new_data

    elif rows:
        new_data = {}
        for row in data:
            row_id = row[0]
            if row_id not in rows:
                raise XLSException('unknown row id: "%s"' % (row_id,))
            if row_id in new_data:
                raise XLSException('duplicate row id: "%s"' % (row_id, ))

            new_data[row_id] = [ data_type(el) for el in row[1:]]

        return new_data

    elif columns:
        new_data = []

        real_columns = data[0]

        if set(real_columns) != set(columns):
            raise XLSException('wrong columns ids: %r' % (real_columns, ))

        for row in data[1:]:
            if len(row) != len(columns):
                raise XLSException('wrong number of elements in row: %r' % (row, ))
            new_data.append(dict(zip(real_columns, [ data_type(el) for el in row])))
        return new_data

    return data


def load_table_for_enums(filename, rows_enum, columns_enum, sheet_index=0, encoding='utf-8', data_type=lambda x: x):

    if issubclass(rows_enum, rels.Relation):
        rows_values = zip(*rows_enum.select('name'))[0]
        rows_items = rows_enum.select('value', 'name')
    else:
        rows_values = rows_enum._ID_TO_STR.values()
        rows_items = rows_enum._ID_TO_STR.items()

    if issubclass(columns_enum, rels.Relation):
        columns_values = zip(*columns_enum.select('name'))[0]
        columns_dict = dict(columns_enum.select('name', 'value'))
    else:
        columns_values = columns_enum._ID_TO_STR.values()
        columns_dict = columns_enum._STR_TO_ID

    data = load_table(filename=filename, sheet_index=sheet_index, encoding=encoding,
                      rows=rows_values,
                      columns=columns_values,
                      data_type=data_type)

    result = dict( (row_id,
                    dict( (columns_dict[column_str], column_value)
                          for column_str, column_value in data[row_str].items()) )
                    for row_id, row_str in rows_items)

    return result


def load_table_for_enums_subsets(filename, rows, columns, sheet_index=0, encoding='utf-8', data_type=lambda x: x):

    rows_values = [el.name for el in rows]
    rows_items = [(el.value, el.name) for el in rows]

    columns_values = [el.name for el in columns]
    columns_dict = {el.name: el.value for el in columns}

    data = load_table(filename=filename, sheet_index=sheet_index, encoding=encoding,
                      rows=rows_values,
                      columns=columns_values,
                      data_type=data_type)

    result = dict( (row_id,
                    dict( (columns_dict[column_str], column_value)
                          for column_str, column_value in data[row_str].items()) )
                    for row_id, row_str in rows_items)

    return result
