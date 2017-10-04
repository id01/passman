#include <string>
#include <curl/curl.h>

size_t httpWriteCallback(void *contents, size_t size, size_t nmemb, void *userp) {
	size_t realsize = size*nmemb;
	((std::string*)userp)->append((char*)contents, realsize);
	return realsize;
}

std::string httpRequest(std::string url, std::string toPost) {
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
		res = curl_easy_perform(curl);
	}
	return readBuffer;
}