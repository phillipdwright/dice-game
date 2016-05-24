def inquire(inquiry, default=None):
    """Returns boolean of user input.
    """
    
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError('invalid default answer: {}'.format(default))
    
    tries = 0
    values = {'y': True, 'n': False}
    
    while tries < 7:
        response = input(inquiry + prompt)
        if default is not None and response == '':
            response = default
        for choice in values:
            if response.lower().startswith(choice):
                return values[choice]
        tries += 1
        print('Please enter "yes" or "no" (or "y" or "n"). ')
    
    print("I'm having trouble understanding your responses!")
    response = input('Please enter "yes" if you wish to continue. ')
    if response.lower.startswith('y'):
        return True
    return False

