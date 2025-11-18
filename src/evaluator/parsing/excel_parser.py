
def check_value(cell_address, worksheet, log=True):
    if log:
        write_to_file(f" \n {worksheet[cell_address].value} \n ")
    return worksheet[cell_address].value


def check_data_type(cell_address, worksheet):
    write_to_file(f" \n {worksheet[cell_address].data_type} (__data_type) \n ")
    return worksheet[cell_address].data_type

