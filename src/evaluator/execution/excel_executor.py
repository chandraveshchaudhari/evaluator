

def empty_data_structure():
    data_structure = dict()
    data_structure['Name'] = None
    data_structure['Roll Number'] = None
    data_structure['Result'] = 0
    data_structure['Error Sum'] = 0
    data_structure['Value Sum'] = 0
    data_structure['Formula Sum'] = 0

    return data_structure

try:
    import xlwings as xw
    xlwings_available = True
except ImportError:
    xlwings_available = False

def get_formula_multiengine(file_path, sheet_name, cell_address):
    # Try openpyxl first
    try:
        wb = openpyxl.load_workbook(file_path)
        ws = wb[sheet_name] if sheet_name in wb.sheetnames else wb.active
        cell = ws[cell_address]

        # Case 1: Cell has .formula attribute (rare)
        if hasattr(cell, "formula") and isinstance(cell.formula, str):
            return cell.formula, "openpyxl (cell.formula)"

        # Case 2: cell.value is a string starting with =
        if isinstance(cell.value, str) and cell.value.startswith("="):
            return cell.value, "openpyxl (cell.value)"

        # Case 3: cell.value is an ArrayFormula or object, reject and fall back
        if hasattr(cell.value, 'text'):
            return cell.value.text, "openpyxl (ArrayFormula.text)"

        # Case 4: Unusable object (e.g., openpyxl ArrayFormula), fall through to xlwings
    except Exception as e:
        # Continue to xlwings
        pass

    # Try xlwings if openpyxl didn't return usable formula
    if xlwings_available:
        try:
            app = xw.App(visible=False)
            wb = app.books.open(file_path)
            sht = wb.sheets[sheet_name] if sheet_name in [s.name for s in wb.sheets] else wb.sheets[0]
            formula = sht.range(cell_address).formula
            wb.close()
            app.quit()
            return formula, "xlwings"
        except Exception as e:
            return None, f"xlwings error: {str(e)}"

    return None, "No formula found"




def check_specific_answers(empty_data, column_name, row_number, number_of_question, formula_worksheet, value_worksheet,
                           values_answer_key, formula_answer_key, file_path):
    values_answer_key = values_answer_key or {}
    formula_answer_key = formula_answer_key or {}

    for i in range(number_of_question):
        write_to_file(f"{'-'* 4} \n \n Checking question number: {i+1}")

        cell_address = column_name + str(row_number + i)
        write_to_file(f"        checking cell:     [{cell_address}]  \n ")

        write_to_file(f"Checking formula output for any errors  \n ")
        value = check_value(cell_address, value_worksheet, False)
        is_error_value = value in (
            "#N/A", "#DIV/0!", "#NAME?", "#NULL!", "#NUM!", "#REF!", "#VALUE!", "#####", "Circular Reference"
        )

        if is_error_value:
            write_to_file(
                f"Error detected in value: >>{value}<<  \n "
            )
            empty_data['Error Sum'] += 1
            write_to_file(f"Your ERROR count increased: {empty_data['Error Sum']}  \n ")

        # Proceed with value checking anyway
        if values_answer_key is not None and cell_address in values_answer_key:
            if checking_if_values_are_correct(value, values_answer_key[cell_address]):
                empty_data['Value Sum'] += 1
                write_to_file(f"Your VALUE count increased: {empty_data['Value Sum']}  \n ")
            else:
                write_to_file(
                    f"   Warning: Output {value} of {type(value)} must be as specified in assignment : {values_answer_key[cell_address]}  of {type(values_answer_key[cell_address])}. \n "
                )
        else:
            write_to_file(f"          No output compulsion for this cell. \n ")

        # Proceed with formula checking regardless
        if formula_answer_key is not None and cell_address in formula_answer_key:
            formula_string, engine_used = get_formula_multiengine(file_path=file_path, sheet_name=formula_worksheet.title, cell_address=cell_address)

            try:
                if hasattr(formula_string, 'text'):
                    formula_string = formula_string.text
                elif not isinstance(formula_string, str):
                    formula_string = str(formula_string)
            except Exception as e:
                write_to_file(f"Error parsing formula: {e}\n")

            if not formula_string or not isinstance(formula_string, str):
                write_to_file("Could not retrieve usable formula from any engine.\n")
            else:
                write_to_file(f"Formula found using {engine_used}: {formula_string}\n")

                expected_results = formula_answer_key[cell_address]
                if isinstance(expected_results, str):
                    expected_results = [expected_results]

                formula_upper = formula_string.upper()

                if any(func.upper() in formula_upper for func in expected_results):
                    empty_data['Formula Sum'] += 1
                    write_to_file(f"Your FORMULA count increased: {empty_data['Formula Sum']}  \n ")
                else:
                    write_to_file(
                        f"   Warning: You should have used one of: {', '.join(expected_results)} but you used: {formula_string}.\n "
                    )
        else:
            write_to_file(f"          No formula compulsion for this cell. \n ")

        if cell_address in values_answer_key or cell_address in formula_answer_key:
            empty_data['Result'] += 1
            write_to_file(f"#####Your RESULT count increased: {empty_data['Result']} ###### \n ")


    return empty_data

def checking_if_values_are_correct(returned_value, actual_value):
    if returned_value == None or actual_value == None:
      return False

    if returned_value == actual_value:
        return True

    try:
        temp_returned_value = float(returned_value)
        temp_actual_value = float(actual_value)

        if temp_returned_value == temp_actual_value:
            return True
    except ValueError:
        pass

    if isinstance(actual_value, list):
      if returned_value in actual_value:
        return True

    if returned_value in ("True", "TRUE", "true", True) and actual_value in ("True", "TRUE", "true", True):
        return True

    elif returned_value in ("False", "FALSE", "false", False) and actual_value in ("False", "FALSE", "false", False):
        return True

    else:
        return False


def evaluate_excel_file(file_path, column_name, row_number, number_of_question, values_answer_key, formula_answer_key,
                        worksheet_name='Answers', student_name_cell='B2', student_roll_no_cell='B3'):
    write_to_file(f"{'~' * 80} \n\n \n ")

    if file_path:
        file_name = file_path.split('/')[-1]
        write_to_file(f" \n \n {'+'* 25} \n Working with {file_name}   \n \n")
    else:
        write_to_file("No file_path  \n ")
        return

    try:
        formula_wb = openpyxl.load_workbook(file_path)
    except:
        write_to_file(f"Could not find the {file_path}  \n ")
        return

    if worksheet_name not in formula_wb.sheetnames:
        new_worksheet = formula_wb.sheetnames[0]
        write_to_file(f"Since '{worksheet_name}' is not there. This tools is using {new_worksheet}  \n ")
        worksheet_name = new_worksheet
    try:
        formula_worksheet = formula_wb[worksheet_name]
    except KeyError:
        write_to_file("sheet named 'Answers' must be there and contain answers.  \n ")
        return

    try:
        value_wb = openpyxl.load_workbook(file_path, data_only=True)
    except:
        write_to_file(f"Could not find the {file_path}  \n ")
        return

    try:
        value_worksheet = value_wb[worksheet_name]
    except KeyError:
        write_to_file("sheet named 'Answers' must be there and contain answers.  \n ")
        return

    try:
        name = check_value(student_name_cell, formula_worksheet)
    except:
        write_to_file(f'Could not find your official Name in B1.  \n ')
        return

    try:
        roll_no = check_value(student_roll_no_cell, formula_worksheet)
    except:
        write_to_file(f'Could not find your roll number in B2.  \n ')
        return

    result_data = check_specific_answers(empty_data_structure(), column_name, row_number, number_of_question,
                                     formula_worksheet, value_worksheet, values_answer_key, formula_answer_key, file_path)

    result_data['Name'] = name
    result_data['Roll Number'] = roll_no

    write_to_file(str(result_data))
    write_to_file(f"{'*' * 80} \n\n \n ")

    return result_data


class CheckExcelFiles:
    def __init__(self, folder_path, formula_answer_key={}, values_answer_key={}):
        self.values_answer_key = values_answer_key
        self.path = folder_path
        self.formula_answer_key = formula_answer_key


    def evaluate_all_excel_files(self, column_name, row_number, number_of_question):
        result_data_list = []
        excel_filenames = get_all_excel_filenames(self.path)

        for filename in excel_filenames:

            file_path = os.path.join(self.path, filename)
            print(file_path)
            data = evaluate_excel_file(file_path, column_name, row_number, number_of_question, self.values_answer_key,
                                       self.formula_answer_key)
            print(data)
            if data:
                result_data_list.append(data)
        df = pd.DataFrame.from_records(result_data_list)

        return df

