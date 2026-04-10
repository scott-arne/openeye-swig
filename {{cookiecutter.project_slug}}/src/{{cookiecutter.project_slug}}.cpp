#include "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}.h"

#include <oechem.h>

namespace {{ cookiecutter.project_prefix }} {

double calculate_molecular_weight(const OEChem::OEMolBase& mol) {
    return OEChem::OECalculateMolecularWeight(mol);
}

} // namespace {{ cookiecutter.project_prefix }}
