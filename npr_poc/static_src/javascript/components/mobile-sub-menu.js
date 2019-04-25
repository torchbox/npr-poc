class MobileSubMenu {
    static selector() {
        return '.js-mobile-menu .js-open-subnav';
    }

    constructor(node) {
        this.node = node;
        this.bindEventListeners();
        
    }

    bindEventListeners() {
        this.node.addEventListener('click', (e) => {
            e.preventDefault();
            this.open();
        });
    }

    open() {
        this.node.nextElementSibling.classList.add('is-visible');
    }
}

export default MobileSubMenu;
