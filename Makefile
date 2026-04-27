.PHONY: build clean run dev list release

build:
	uv sync --dev
	uv run pyinstaller ipvtop.spec --clean --noconfirm

clean:
	rm -rf build dist

run: build
	sudo ./dist/ipvtop $(IFACE)

dev:
	sudo uv run ipvtop $(IFACE)

list:
	uv run ipvtop -l

release:
ifndef VERSION
	$(error VERSION is required. Usage: make release VERSION=0.1.0)
endif
	git tag v$(VERSION)
	git push origin v$(VERSION)
