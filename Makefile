default:
	gcc -g -std=c99 -O0 -Wall lispy.c mpc.c -o lispy && ctags -R

