'''
This script generates RPM packages for custom applications built using NX-SDK.
For more information, please run the script with -h option.
'''

import os, subprocess
import os, subprocess
import argparse
import sys
import shutil

# Paths
if "NXSDK_ROOT" in os.environ:
	nxsdk_path = os.environ["NXSDK_ROOT"]
else:
	nxsdk_path = "/NX-SDK"

if "ENXOS_SDK_ROOT" in os.environ:
	enxos_sdk_path = os.environ["ENXOS_SDK_ROOT"]
else:
	enxos_sdk_path = "/enxos-sdk"

# Export environment
env_file = os.path.join(enxos_sdk_path, "environment-setup-x86-wrsmllib32-linux")
output = subprocess.Popen(". " + env_file + ";env", stdout=subprocess.PIPE, shell=True).communicate()[0]
env = dict((line.split("=", 1) for line in output.splitlines()))
os.environ.update(env)



rpm_root = os.path.join(enxos_sdk_path, "sysroots/x86_64-wrlinuxsdk-linux/usr/src/rpm")

# Default values for arguments
default_app_source = os.path.join(nxsdk_path, "examples")
default_app_desc="RPM package for custom application"
default_app_target = os.path.join(nxsdk_path, "bin")
default_app_version = "1.0"
release_version = "1.0.0"

# Spec file parameters
custom_spec_file_path = os.path.join(nxsdk_path, "scripts/template.spec")
app_name_str = "APP_NAME"
app_source_str = "APP_SOURCE"
app_target_str = "APP_TARGET"
app_desc_str = "APP_DESC"
app_version_str = "APP_VERSION"
release_version_str = "RELEASE_VERSION"
nxsdk_root_str = "NXSDK_ROOT"
spec_file_params = {}

# Help string

help_string = "This script generates RPM packages for custom applications built using NX-SDK.\
Please export the path for NX-SDK as environment variable NXSDK_ROOT and \
ENXOS-SDK as environment variable ENXOS_SDK_ROOT before calling the script.\
If not found, the script assumes NX-SDK to be present at the following location /NX-SDK \
and ENXOS-SDK to be present at /enxos-sdk"

def build_rpm(spec_file_path):
	os.environ["RPM_ROOT"] = rpm_root
	os.system("rpm -ba " + spec_file_path)
	rpm_file_name = spec_file_params[app_name_str] + "-" + spec_file_params[app_version_str] + \
		"-" + spec_file_params[release_version_str] + ".x86_64.rpm"
	rpm_file_path = os.path.join(rpm_root, "RPMS/x86_64/", rpm_file_name)
	return rpm_file_path


def copy_files(spec_file_path, rpm_file_path):
	rpm_dest = os.path.join(nxsdk_path, "rpm/RPMS/")
	shutil.copy(rpm_file_path, rpm_dest)
	spec_file_dest = os.path.join(nxsdk_path, "rpm/SPECS/")
	shutil.copy(spec_file_path, spec_file_dest)
	print "\nSPEC file: " + spec_file_dest + os.path.basename(spec_file_path)
	print "RPM file : " + rpm_dest + os.path.basename(rpm_file_path)


def write_spec():
	spec_file_path = os.path.join(rpm_root, "SPECS/", spec_file_params[app_name_str] + ".spec")

	spec_file = open(spec_file_path, 'w')
        spec_file.write("### Spec file auto-generated by rpm_gen.py...\n\n")
	for macro in spec_file_params:
		line = "%define " + macro + " " + spec_file_params[macro] + "\n\n"
		spec_file.write(line)
	custom_spec_file = open(custom_spec_file_path, 'r')
	lines = custom_spec_file.readlines()
	spec_file.writelines(lines)
	return spec_file_path


def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=help_string)
	parser.add_argument("name", help="Name of the application binary or the file name in case of python")
	parser.add_argument("-s", "--source", default=default_app_source,
		help="Path of the folder where application source files are present")

	group = parser.add_mutually_exclusive_group()
	group.add_argument("-u", "--use_source_as_target", action = "store_true", default= False,
		help="If the source file is the same as the executable")
	group.add_argument("-t", "--target", default=default_app_target,
		help="Path where the application binary or the python file is present")

	parser.add_argument("-d", "--description", default=default_app_desc,
		help="Application Description")
	parser.add_argument("-v", "--version", default=default_app_version,
		help="Application Version")

	args = parser.parse_args()

	if not args.use_source_as_target:
		target = os.path.join(args.target, args.name)
	else:
		target = os.path.join(args.source, args.name)

	target = os.path.abspath(target)
	if not os.path.isfile(target):
		parser.print_help()
		sys.exit("Target " + target + " not found")

	spec_file_params[app_name_str] = args.name
	spec_file_params[app_desc_str] = args.description
	spec_file_params[app_source_str] = os.path.abspath(args.source)
	spec_file_params[app_target_str] = target
	spec_file_params[app_version_str] = args.version
        spec_file_params[release_version_str] = release_version
        spec_file_params[nxsdk_root_str] = nxsdk_path 
 
	print "#"*100
	print "Generating rpm package..."
	spec_file_path = write_spec()
	rpm_file_path = build_rpm(spec_file_path)
	print "RPM package has been built"
	print "#"*100
	copy_files(spec_file_path, rpm_file_path)

main()


