// Simple video modal which doesn't use a third party library like lightbox

// Assumes a strcuture as follows
// <div class="js-video-modal">
//     <a class="js-video-modal-open">Open video</a>
//     <div class="js-modal-window">
//         <a class="js-modal-close">close</a>
//         Video iframe embed
//     </div>
// </div>

class VideoModal {

    static selector() {
        return '.js-video-modal';
    }

    constructor(node) {
        this.modal = node;
        this.modalOpen = this.modal.querySelector('.js-modal-open');
        this.modalWindow = this.modal.querySelector('.js-modal-window');
        this.modalClose = this.modal.querySelector('.js-modal-close');
        this.iframe = this.modal.querySelector('iframe');
        this.src = this.iframe.getAttribute('src');
        this.bindEvents();
    }

    bindEvents() {
        this.modalOpen.addEventListener('click', (e) => {
            e.preventDefault();
            this.modalWindow.classList.add('open');
            this.iframe.setAttribute('src', this.src);
        });

        this.modalClose.addEventListener('click', (e) => {
            e.preventDefault();
            this.modalWindow.classList.remove('open');
            // stops video playing when window is closed
            this.iframe.setAttribute('src', '');
        });
    }
}

export default VideoModal;
