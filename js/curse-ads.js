// Ad blocking note

var target = document.querySelector('.promo-container');

function removeNonClassAttributes(element) {
    var attributes = element.attributes;
    var i = attributes.length;
    while (i--) {
        var attr = attributes.item(i);
        if (attr.name !== 'class')
            element.removeAttributeNode(attr);
    }
}

function showBlockNote() {
    var blockNote = document.querySelector('.promo-container .block-note');
    removeNonClassAttributes(target);
    removeNonClassAttributes(blockNote);
    blockNote.classList.add('block-note-show');
    blockNote.setAttribute('style', 'display: flex !important');
    target.setAttribute('style', 'display: block !important');
}

function handleAttributeMutation(target, attribute) {
    var classes = target.classList;
    if (!classes.contains('promo-container') && !classes.contains('promo-content')) {
        return;
    }
    if (attribute === 'hidden') {
        showBlockNote();
    }
}

function handleChildRemoval(children) {
    children.forEach(
        function (child) {
            if (child.classList.contains('promo-content')) {
                showBlockNote();
            }
        }
    );
}

// create an observer instance
var observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
        if (mutation.type === 'attributes') {
            handleAttributeMutation(mutation.target, mutation.attributeName);
        } else if (mutation.type === 'childList') {
            handleChildRemoval(mutation.removedNodes);
        }
    });
});

var observerConfig = {attributes: true, childList: true, characterData: true, subtree: true};
if (target)
    observer.observe(target, observerConfig);

window.isDoneLoading = false;
(window.attachEvent || window.addEventListener)('message', function (e) {
    document.querySelector('body').classList.add('loading-done');
    window.isDoneLoading = true;
});

setTimeout(
    function () {
        if (!window.isDoneLoading) {
            document.querySelector('body').classList.add('loading-done');
        }
    },
    1000
);

$(document).ready(function() {
    window.themeSwitchToggle();
});
