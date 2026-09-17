let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = with pkgs; [
    (python312.withPackages (python-pkgs: with python-pkgs; [
      pyopengl
      glfw
      numpy
      opencv4
      pandas
      pillow
    ]))
  ];
}
