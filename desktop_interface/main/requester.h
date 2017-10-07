#define COOKIEFILE "/tmp/passmancookie.txt"
#include <string>
#include <curl/curl.h>

size_t httpWriteCallback(void *contents, size_t size, size_t nmemb, void *userp) {
	size_t realsize = size*nmemb;
	((std::string*)userp)->append((char*)contents, realsize);
	return realsize;
}

std::string httpRequest(std::string url, std::string toPost, int mode=0) {
	CURL *curl;
	CURLcode res;
	std::string readBuffer;
	curl_global_init(CURL_GLOBAL_DEFAULT);
	curl = curl_easy_init();
	if (curl) {
		curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
		curl_easy_setopt(curl, CURLOPT_POSTFIELDS, toPost.c_str());
		curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, httpWriteCallback);
		curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
		switch (mode) {
			case 1: curl_easy_setopt(curl, CURLOPT_COOKIEJAR, COOKIEFILE); break; // Write cookies
			case 2: curl_easy_setopt(curl, CURLOPT_COOKIEFILE, COOKIEFILE); break; // Read cookies
			default: break; // Do nothing
		}
		res = curl_easy_perform(curl);
	}
	curl_easy_cleanup(curl);
	return readBuffer;
}