window.initReadingTimePanel = function(readingTimePanelID) {
    const form = document.querySelector('[data-edit-form]');
    const readingTime = document.getElementById(readingTimePanelID);
    const readingTimeDataElement = readingTime.querySelector('[data-reading-time-data]');
    const refreshReadingTimeButton = readingTime.querySelector('.reading-time-panel-data .icon.middle');
    const previewSidePanel = document.querySelector(
        '[data-side-panel="preview"]',
    );

    // Preview side panel is not shown if the object does not have any preview modes
    if (!previewSidePanel) return;

    // The previewSidePanel is a generic container for side panels,
    // the content of the preview panel itself is in a child element
    const previewPanel = previewSidePanel.querySelector('[data-preview-panel]');
    const previewUrl = previewPanel.dataset.action;
    // Start with an empty payload so that when checkAndUpdatePreview is called
    // for the first time when the panel is opened, it will always update the preview
    let oldPayload = '';
    let hasPendingUpdate = false;
    let previewPanelOpen = !previewSidePanel.hasAttribute('hidden');

    const hasChanges = () => {
      const newPayload = new URLSearchParams(new FormData(form)).toString();
      const changed = oldPayload !== newPayload;

      oldPayload = newPayload;

      return changed;
    };

    const debounce = (fn, delay) => {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                timeoutId = null;
                fn.apply(this, args);
            }, delay);
        };
    };
    

    const _updateReadingTime = () => {


        if (hasPendingUpdate) return;
        hasPendingUpdate = true;

        const payload = new URLSearchParams({
            mode: "reading_time"
        }).toString();

        const url = `${previewUrl}?${payload}`;

        return fetch(url, {
            method: "GET",
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              "Content-Type": "application/json",
              "Accept": "application/json",
            },
        }).then(function(response) {
            if (readingTimeDataElement.classList.contains('loading-mask')) {
                readingTimeDataElement.classList.remove('loading-mask', 'loading');
            }
            return response.json();
        }).then(function(data) {
            formObserver.disconnect();
            readingTimeDataElement.innerHTML = data.reading_time;
            formObserver.observe(form, {childList: true, subtree: true});
            hasPendingUpdate = false;
        }).catch(function(error) {
            console.error("Error:", error);
            hasPendingUpdate = false;
        });
    };

    const updateReadingTime = () => {
        readingTimeDataElement.classList.add('loading-mask', 'loading');
        if (previewPanelOpen) {
            return _updateReadingTime();
        } else {
            return fetch(previewUrl, {
                method: 'POST',
                body: new FormData(form),
            }).then(response => {
                if (response.ok) {
                    return _updateReadingTime();
                }
                if (readingTimeDataElement.classList.contains('loading-mask')) {
                    readingTimeDataElement.classList.remove('loading-mask', 'loading');
                }
                return Promise.reject(response);
            })
        }
    };

    const checkChangesAndUpdateReadingTime = () => {
        if (hasChanges()) {
            updateReadingTime();
        }
    }

    const iFrameWrapper = previewSidePanel.querySelector('.preview-panel__wrapper');
    const iFrameObserverFn = function(mutationsList, observer) {
        for (let mutation of mutationsList) {
            if (mutation.type === 'childList' && mutation.addedNodes.length) {
                let shouldUpdate = true;
                // Check if we updated the iframe with the preview panel
                for (let node of mutation.addedNodes) {
                    if (node === previewPanel) {
                        shouldUpdate = false;
                        break;
                    }
                }
                if (shouldUpdate) {
                    updateReadingTime();
                }
                return;
            }
        }
    };
    
    const checkChangesAndUpdateReadingTimeDebounced = debounce(checkChangesAndUpdateReadingTime, 500);
    const formObserver = new MutationObserver(checkChangesAndUpdateReadingTimeDebounced);
    const iFrameObserver = new MutationObserver(iFrameObserverFn);

    if (!previewPanelOpen) {
        formObserver.observe(form, {childList: true, subtree: true});
    }

    previewSidePanel.addEventListener('show', function() {
        previewPanelOpen = true;
        formObserver.disconnect();
    });

    previewSidePanel.addEventListener('hide', function() {
        previewPanelOpen = false;
        formObserver.observe(form, {childList: true, subtree: true});
    });


    iFrameObserver.observe(iFrameWrapper, {childList: true});
    refreshReadingTimeButton.addEventListener('click', function() {
        // loading-mask loading
        readingTimeDataElement.classList.add('loading-mask', 'loading');
        updateReadingTime().then(() => {
            readingTimeDataElement.classList.remove('loading-mask', 'loading');
        });
    });
};
