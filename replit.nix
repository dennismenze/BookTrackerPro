{pkgs}: {
  deps = [
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
