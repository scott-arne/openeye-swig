#ifndef {{ cookiecutter.project_prefix }}_H
#define {{ cookiecutter.project_prefix }}_H

// Version information
#define {{ cookiecutter.project_prefix }}_VERSION_MAJOR {{ cookiecutter.initial_version.split('.')[0] }}
#define {{ cookiecutter.project_prefix }}_VERSION_MINOR {{ cookiecutter.initial_version.split('.')[1] }}
#define {{ cookiecutter.project_prefix }}_VERSION_PATCH {{ cookiecutter.initial_version.split('.')[2] }}

#include <oechem.h>

namespace {{ cookiecutter.project_prefix }} {

/// \brief Calculate the molecular weight of a molecule.
///
/// Passes the molecule natively from Python to C++ via SWIG typemaps,
/// then delegates to OEChem's OECalculateMolecularWeight.
///
/// \param mol Reference to an OEMolBase object.
/// \returns Molecular weight in Daltons.
double calculate_molecular_weight(const OEChem::OEMolBase& mol);

} // namespace {{ cookiecutter.project_prefix }}

#endif // {{ cookiecutter.project_prefix }}_H
