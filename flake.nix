# flake.nix
{
  description = "Einstein Field AI - Forensic Semiotic Audit Platform (FSA)";

  inputs = {
    # Pinning nixpkgs to the latest stable release (25.05 as of Oct 2025)
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Define the Python environment (Python 3.11) with core dependencies
        pythonEnv = pkgs.python311.withPackages (p: with p; [
          # Core Libraries
          pydantic
          requests
          tenacity
          python-dotenv
          # Ingestion
          arxiv
          pymupdf # (fitz)
          # LLM, Structured Output & Observability
          openai
          instructor
          langfuse
        ]);

      in {
        # The development shell
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.git
          ];

          shellHook = ''
            echo "FSA Deterministic Environment Loaded."
            # Ensure the python executable points to the Nix environment
            export PATH="${pythonEnv}/bin:$PATH"

            # Load environment variables if .env exists
            if [ -f .env ]; then
              echo "Loading .env file..."
              export $(grep -v '^#' .env | xargs)
            fi
          '';
        };
      });
}
