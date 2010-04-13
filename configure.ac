AC_INIT([blinq], [0.1.1], [])
AM_INIT_AUTOMAKE([1.9])

AC_CONFIG_MACRO_DIR([m4])

AM_PATH_PYTHON([2.4])

BLINQ_PYTHON_DIR=`(
	case $prefix in
	     NONE) prefix=$ac_default_prefix ;;
	     *) ;;
	esac
	eval echo $(eval echo $pythondir)
)`
AC_SUBST(BLINQ_PYTHON_DIR)


BLINQ_MODULES_DIR=`(
	case $prefix in
	     NONE) prefix=$ac_default_prefix ;;
	     *) ;;
	esac
	eval echo $(eval echo $pkgpythondir)
)`
AC_SUBST(BLINQ_MODULES_DIR)

BLINQ_DATA_DIR=`(
	case $prefix in
	     NONE) prefix=$ac_default_prefix ;;
	     *) ;;
	esac
	eval echo $(eval echo $datadir)/blinq
)`
AC_SUBST(BLINQ_DATA_DIR)

AC_CONFIG_FILES([
Makefile
blinq/Makefile
blinq/reqs/Makefile
])

AC_OUTPUT

echo "
blip-$VERSION:

	Prefix:     ${prefix}
	Python:     ${BLINQ_PYTHON_DIR}
	Modules:    ${BLINQ_MODULES_DIR}
	Data files: ${BLINQ_DATA_DIR}
"
