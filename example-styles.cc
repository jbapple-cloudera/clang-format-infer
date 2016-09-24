#include <cstdlib>
#include <iostream>
#include <system_error>

using namespace ::std;

#include <unistd.h>

#include <clang/Format/Format.h>

using namespace ::clang::format;

string StoreInFile(const string& data) {
  char result[] = "/tmp/XXXXXX";
  const int fd = mkstemp(result);
  if (-1 == fd) throw system_error(make_error_code(errc(errno)));
  ssize_t total_written = 0;
  while (total_written < static_cast<ssize_t>(data.size())) {
    const ssize_t written =
        write(fd, data.data() + total_written, data.size() - total_written);
    if (-1 == written) throw system_error(make_error_code(errc(errno)));
    total_written += written;
  }
  return result;
}

int main() {
  static constexpr decltype(&getGoogleStyle) MULTI_LANGUAGE_STYLES[] = {
      getGoogleStyle, getChromiumStyle};
  static constexpr decltype(&getLLVMStyle) SINGLE_LANGUAGE_STYLES[] = {
      getLLVMStyle, getMozillaStyle, getWebKitStyle, getGNUStyle};
  static constexpr decltype(FormatStyle::LK_Cpp) LANGUAGES[] = {FormatStyle::LK_Cpp,
      FormatStyle::LK_Java, FormatStyle::LK_JavaScript, FormatStyle::LK_Proto,
      FormatStyle::LK_TableGen};

  for (const auto& multi_style : MULTI_LANGUAGE_STYLES) {
    for (const auto& language : LANGUAGES) {
      const string printed_style = configurationAsText(multi_style(language));
      cout << StoreInFile(printed_style) << endl;
    }
  }
  for (const auto& style : SINGLE_LANGUAGE_STYLES) {
    const string printed_style = configurationAsText(style());
    cout << StoreInFile(printed_style) << endl;
  }
}
