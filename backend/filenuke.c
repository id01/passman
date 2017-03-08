#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

int get_file_size(char * myfile)
{
	FILE * fp = fopen(myfile, "r");
	if (fp == NULL) { return -1; }
	fseek(fp, 0, SEEK_END);
	int length = ftell(fp);
	fclose(fp);
	return length;
}

void randomize_file(char * myfile, int length)
{
	srand(clock());
	FILE * fp = fopen(myfile, "w");
	if (fp == NULL) { return; }
	for (int i=0; i<length; i++)
	{
		fputc(rand()%256, fp);
	}
	fclose(fp);
}

void blank_file(char * myfile, int length)
{
	FILE * fp = fopen(myfile, "w");
	if (fp == NULL) { return; }
	for (int i=0; i<length; i++)
	{
		fputc(0, fp);
	}
	fclose(fp);
}

void printerror(unsigned char code)
{
	switch(code)
	{
		case 0: printf("Execution success.\n"); break;
		case 1: printf("File not found.\n"); break;
		case 254: printf("Syntax error.\n"); break;
		default: printf("Unknown error.\n");
	}
}

int main(int argc, char * argv[])
{
	if (argc < 2) { printerror(254); return 254; }
	int size = get_file_size(argv[1]);
	if (size < 0) { printerror(1); return 1; }
	randomize_file(argv[1], size);
	blank_file(argv[1], size+1);
	unlink(argv[1]);
	printerror(0); return 0;
}