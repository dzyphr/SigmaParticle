#include <bits/stdc++.h>
#include <vector>
using std::cout, std::string, std::vector;
void makeNewContractFrame(string ContractName);
void echoContractName(string ContractName);
int main(int argc, char* argv[])
{
	if (argc < 2)
	{
		cout << "enter the Contract Name";
	}
	else if (argc >= 2)
	{
		makeNewContractFrame(argv[1]);
		echoContractName(argv[1]);
	}
}

void makeNewContractFrame(string ContractName)
{
	string command = "cp -r basic_framework " + ContractName;
	system(command.c_str());	
}

void echoContractName(string ContractName)
{
	string command = "echo \'ContractName=\"" +  ContractName + "\"' >> " + ContractName + "/.env";
	system(command.c_str());
}
