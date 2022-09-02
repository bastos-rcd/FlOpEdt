from TTapp.FlopModel import iis_files_path

def analyse_contraintes(ttmodel):

    ilp_bookname = ttmodel.iis_filename()

    d={}

    with open(ilp_bookname) as file:
        for s in file:
            is_a_line = len(s.split(':')) == 2
            if is_a_line:
                cle, contrainte_math = s.split(':')
                contrainte_math = contrainte_math.split('\n')[0]
                if '>=' in contrainte_math:
                    operateur = '>='
                elif '<=' in contrainte_math:
                    operateur = "<="
                else:
                    operateur = '='
                somme, valeur = contrainte_math.split(operateur)
                somme = somme[1:-1].replace("'", "")
                positifs = somme.split(' + ')
                negatifs = somme.split(' - ')

                if len(negatifs) == 1:
                    negatifs = []

                elif len(positifs) == 1:
                    positifs = []

                if negatifs:
                    if negatifs[0][0] != '-':
                        positifs.append(negatifs.pop(0))

                if positifs:
                    if positifs[0][0] == '-':
                        negatifs.append(positifs.pop(0)[2:])
                positifs = convert_coeff_vars_list_in_couples_list(positifs, ttmodel)
                negatifs = convert_coeff_vars_list_in_couples_list(negatifs, ttmodel)
                d[int(cle)] = positifs, negatifs, operateur, valeur
    return d


def convert_coeff_vars_list_in_couples_list(coef_vars_list, ttmodel):
    result = []
    for p in coef_vars_list:
        coeff_var = p.split(' ')
        if len(coeff_var) == 1:
            var_id = int(coeff_var[0])
            var = ttmodel.vars[var_id]
            result.append((1., var.id, var.name))

        else:
            c, var_id_str = coeff_var
            var_id = int(var_id_str)
            var = ttmodel.vars[var_id]
            result.append((float(c), var.id, var.name))
    return result


def write_translated_file(dico, filename):
    with open(filename, 'w') as file:
        for key, value in dico.items():
            row = f"{key}: \n"
            positifs, negatifs, operateur, valeur = value
            if positifs:
                row += "\n + ".join([f"{positif[0]} * {positif[2]}({positif[1]})" for positif in positifs])
            if negatifs:
                row += "\n - " + "\n - ".join([f"{negatif[0]} * {negatif[2]}({negatif[1]})" for negatif in negatifs])
            row += f"\n{operateur} {valeur} \n\n"
            file.write(row)


def translate_ilp_file(ttmodel, filename=None):
    dico = analyse_contraintes(ttmodel)
    if filename is None:
        filename = "%s/translated_IIS%s.ilp" % (iis_files_path, ttmodel.iis_filename_suffixe())
    write_translated_file(dico, filename)