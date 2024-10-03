{pkgs}: {
  deps = [
    pkgs.geckodriver
    pkgs.sqlite-interactive
    pkgs.pg-dump-anon
    pkgs.rustc
    pkgs.pkg-config
    pkgs.openssl
    pkgs.libxcrypt
    pkgs.libiconv
    pkgs.cargo
    pkgs.postgresql
  ];
}
