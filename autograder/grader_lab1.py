def grade_solution(student_output, solution):
    grades = {}

    for field in solution:
        if solution[field]['match'] == 'ignored':
            continue
        grades[field] = {'match': False, 'expected': '', 'obtained': ''}
        
        if solution[field]['match'] == 'exact':
            if field in student_output:
                grades[field]['match'] = solution[field]['value'] == student_output[field]['value']       
            else:
                grades[field]['match'] = False
            if not grades[field]['match']:  # add expected output if not matched
                if field in student_output: 
                    grades[field]['expected'] = solution[field]['value']
                    grades[field]['obtained'] = student_output[field]['value'] if field in student_output else ''
                else:
                    grades[field]['expected'] = solution[field]['value']
        elif solution[field]['match'] == 'contained':
            correct_lines = set(solution[field]['value'])
            if field in student_output:
                output_lines = set(student_output[field]['value'])
                grades[field]['match'] = output_lines == correct_lines
            else:
                grades[field]['match'] = False
            if not grades[field]['match']:  # add expected output if not matched
                if field in student_output:
                    grades[field]['expected'] = correct_lines.difference(output_lines)
                    grades[field]['obtained'] = output_lines.difference(correct_lines)
                else:
                    grades[field]['expected'] = correct_lines
                    grades[field]['obtained'] = set()
        else:
            pass
    
    return grades


def generate_expected_output(subtask_info):
    expected_lines = [f"# {subtask_info['name']}"]
    fields = subtask_info['expected_output_fields']
    if subtask_info['name'].startswith('HEURISTIC'):
        expected_lines += [f"[CONDITION]: {i}" for i in fields['CONDITIONS']['value']]
        expected_lines.append(f"[CONCLUSION]: {fields['CONCLUSION']['value']}")
    else:
        for element in ['FOUND_SOLUTION', 'STATES_VISITED', 'PATH_LENGTH', 'TOTAL_COST', 'PATH']:
            expected_lines.append(f"[{element}]: {fields[element]['value']}")
    return '\n'.join(expected_lines)


def parse_output(output, correct_output=False):
    output_lines = output.split('\n')
    subtask_output = {}

    for line in output_lines:
        if line.startswith('# '):
            subtask = line.strip().split()[1].upper()
            if line.startswith('# A-STAR') or line.startswith('# HEURISTIC'):
                heuristic = line.strip().split()[2].split('.')[0].lower()
                subtask += f'-{heuristic}'
            else:
                heuristic = None
        elif line.startswith('['):
            if line.startswith('[CONDITION]:'):
                if 'CONDITIONS' not in subtask_output:
                    subtask_output['CONDITIONS'] = {'value': []}
                    if correct_output:
                        subtask_output['CONDITIONS']['match'] = 'contained'
                subtask_output['CONDITIONS']['value'].append(' '.join(line.strip().split()[1:]))
            else:
                field = line.strip().split()[0][1:-2]
                subtask_output[field] = {'value': []}
                if correct_output:
                    if field in ['PATH', 'PATH_LENGTH', 'STATES_VISITED'] and subtask in ['UCS', 'A-STAR']:
                        subtask_output[field]['match'] = 'ignored'
                    else:
                        subtask_output[field]['match'] = 'exact'
                subtask_output[field]['value'] = ' '.join(line.strip().split()[1:])
        else:
            break

    return subtask_output

