def read_configuration(file):
    f = open(file, "r")
    config = f.read()
    config = config.replace('"', '\"')
    config = config.replace('\n', '')
    config = config.replace('\t', '')
    config = config.replace(' ', '')
    return config
