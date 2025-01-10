document.addEventListener("DOMContentLoaded", () => {
    // Seleziona gli elementi principali del DOM
    const form = document.getElementById("prenotazione-form");
    const confermaPulsante = document.getElementById("conferma");
    const modificaPulsante = document.getElementById("modifica");
    const cancellaPulsante = document.getElementById("elimina");
	const calcoloPulsante = document.getElementById("calcolo");


    // Controlla se il form esiste nel DOM
    if (!form) {
        console.error("Il form con ID 'prenotazione-form' non è stato trovato!");
        return;
    }

	 // Variabili per gestire lo stato delle prenotazioni
    const codiciPrenotazione = []; // Memorizza i codici prenotazione generati
    let codicePrenotazioneCorrente = null; // Codice prenotazione attualmente in modifica

    // Funzione per resettare il form
    const resettaForm = () => {
        form.reset(); // Resetta tutti i campi del form
        codicePrenotazioneCorrente = null; // Resetta il codice prenotazione corrente
        attivaPulsanti(false); // Riabilita i pulsanti principali
    };

    // Funzione per abilitare o disabilitare i pulsanti
    const attivaPulsanti = (disable) => {
		confermaPulsante.disabled = disable;
        cancellaPulsante.disabled = disable;
	};

    // Funzione per validare i dati del form
    const validareForm = () => {
        // Recupera i valori dai campi del form
        const ritiroNome = document.getElementById("ritiro_nome").value.trim();
        const ritiroEmail = document.getElementById("ritiro_email").value.trim();
        const ritiroTelefono = document.getElementById("ritiro_telefono").value.trim();
        const citta = document.getElementById("citta").value;
        const ritiroIndirizzo = document.getElementById("ritiro_indirizzo").value.trim();
        const ritiroDataora = document.getElementById("ritiro_dataora").value;
        const consegnaNome = document.getElementById("consegna_nome").value.trim();
        const consegnaEmail = document.getElementById("consegna_email").value.trim();
        const consegnaTelefono = document.getElementById("consegna_telefono").value.trim();
        const consegnaIndirizzo = document.getElementById("consegna_indirizzo").value.trim();
        const pesoPacco = parseFloat(document.getElementById("peso_pacco").value);

        // Controlla che tutti i campi siano compilati
        if (!ritiroNome || !ritiroEmail || !ritiroTelefono || !citta || !ritiroIndirizzo || 
            !ritiroDataora || !consegnaNome || !consegnaEmail || !consegnaTelefono || 
            !consegnaIndirizzo || isNaN(pesoPacco)) {
            mostraNotifica("Tutti i campi devono essere compilati correttamente.", "info");
            return false;
        }
		
		// Validazione dell'email
		if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(ritiroEmail) || !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(consegnaEmail)) {
			mostraNotifica("Inserisci un indirizzo email valido.", "info");
		return false;
		}

		// Validazione del numero di telefono
		if (!/^\d{8,15}$/.test(ritiroTelefono) || !/^\d{8,15}$/.test(consegnaTelefono)) {
			mostraNotifica("Il numero di telefono deve contenere solo cifre e avere tra 8 e 15 caratteri.", "info");
		return false;
		}

        // Validazione del peso del pacco 
        if (pesoPacco <= 0) {
            mostraNotifica("Il peso del pacco deve essere un numero positivo.","info");
            return false;
        }
		
		if (pesoPacco > 100) {
			mostraNotifica("Il peso massimo consentito è di 100 kg.", "error");
			return false;
		}
	
		// Validazione della data e ora di ritiro
		const now = new Date();
		const ritiroDataoraObj = new Date(ritiroDataora);

		
		if (ritiroDataoraObj - now < 60 * 60 * 1000) {
			mostraNotifica("La data e ora di ritiro devono essere almeno un'ora successive all'orario attuale.", "info");
		return false;
		}

		// Controlla orari lavorativi
		const ritiroOra = ritiroDataoraObj.getHours();
		const ritiroMinuti = ritiroDataoraObj.getMinutes();
		if ((ritiroOra < 8) || (ritiroOra === 17 && ritiroMinuti > 0) || ritiroOra > 17) {
			mostraNotifica("L'orario di ritiro deve essere tra le 8:00 e le 17:00.", "info");
		return false;
		}

		// Controlla che non sia domenica
		if (ritiroDataoraObj.getDay() === 0) { 
			mostraNotifica("Le prenotazioni non possono essere fatte di domenica.", "info");
		return false;
		}

		// Controlla che il giorno non sia un festivo
		const festivi = [
		"2024-01-01", // Capodanno
		"2024-04-25", // Festa della Liberazione
		"2024-05-01", // Festa dei Lavoratori
		"2024-06-02", // Festa della Repubblica
		"2024-12-25", // Natale
		"2024-12-26"  // Santo Stefano
		];
		const ritiroData = ritiroDataoraObj.toISOString().split("T")[0]; // Ottieni solo la parte della data
		if (festivi.includes(ritiroData)) {
			mostraNotifica("Le prenotazioni non possono essere fatte nei giorni festivi.", "info");
		return false;
		}
        return true;
    };


		// Funzione per calcolare il costo della spedizione
		const calcoloSpedizione = () => {
        const pesoPacco = parseFloat(document.getElementById("peso_pacco").value);
        if (isNaN(pesoPacco) || pesoPacco <= 0) {
            mostraNotifica("Inserisci un peso valido.", "info");
            return;
        }

        const tariffe = [
            { min: 0, max: 1, prezzo: 13.52 },
            { min: 2, max: 3, prezzo: 15.55 },
            { min: 4, max: 5, prezzo: 18.00 },
            { min: 6, max: 10, prezzo: 19.60 },
            { min: 11, max: 20, prezzo: 22.13 },
            { min: 21, max: 30, prezzo: 23.23 },
            { min: 31, max: 40, prezzo: 26.60 },
            { min: 41, max: 50, prezzo: 29.00 },
            { min: 51, max: 75, prezzo: 34.00 },
            { min: 76, max: 100, prezzo: 45.00 }
        ];

        const tariffa = tariffe.find(t => pesoPacco >= t.min && pesoPacco <= t.max);
        if (tariffa) {
			const formattaPrezzo = tariffa.prezzo.toFixed(2).replace(".", ",");
            mostraNotifica(`Il costo della spedizione è: € ${formattaPrezzo}`, "info");
        } else {
            mostraNotifica("Il peso massimo consentito è di 100 kg.", "error");
        }
    };

		calcoloPulsante.addEventListener("click", (event) => {
        event.preventDefault();
        calcoloSpedizione();
    });


		// Funzione per mostrare notifiche
		const notificaArea = document.getElementById("area-notifica");
		if (!notificaArea) {
			console.error("Elemento area-notifica non trovato nel DOM!");
			return;
		}

		
		const mostraNotifica = (message, type = "info") => {
		const notificaArea = document.getElementById("area-notifica");
		if (!notificaArea) return;
			
		while (notificaArea.children.length >= 3) {
			notificaArea.removeChild(notificaArea.firstChild);
		}

		const notifica = document.createElement("div");
		notifica.className = `notifica ${type}`;
		notifica.textContent = message;

		// Aggiungi la notifica all'area delle notifiche
		notificaArea.appendChild(notifica);

		// Rimuovi la notifica dopo che l'animazione è terminata
		notifica.addEventListener("animationend", () => {
		notifica.remove();
		});
	};


	// Invio dati della prenotazione al backend tramite api rest
	const inviaPrenotazione = async (datiPrenotazione) => {
		try {
			const risposta = await fetch("/api/prenotazioni", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(datiPrenotazione),
			});

			if (!risposta.ok) {
				const errorData = await risposta.json();
				throw new Error(errorData.error || `Errore HTTP: ${risposta.status} (${risposta.statusText})`);
			}
	
			const data = await risposta.json();
			mostraNotifica(`Prenotazione confermata! Codice: ${data.codice_prenotazione}`, "success");
			return data;

		} catch (error) {
			console.error("Errore durante l'invio della prenotazione:", "error");
			mostraNotifica("Errore di rete o server non raggiungibile. Riprova più tardi.", "error");
		}
	};

	// Invio dati per aggiornare la prenotazione
	const modificaPrenotazione = async (bookingCode, updatedData) => {
		// Validazione iniziale
		if (!bookingCode) {
			console.error("Nessun codice prenotazione fornito.");
			mostraNotifica("Codice prenotazione non fornito.", "error");
			return;
		}

		if (!updatedData || Object.keys(updatedData).length === 0) {
			console.error("Dati aggiornati mancanti o vuoti.");
			mostraNotifica("I dati aggiornati sono mancanti o incompleti.", "error");
			return;
		}

		
		attivaPulsanti(true); // Disabilita i pulsanti Conferma e cancella
		
		try {
			const risposta = await fetch(`/api/prenotazioni/${bookingCode}`, {
				method: "PUT",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(updatedData),
			});

			if (!risposta.ok) {
				const errorData = await risposta.json();
				throw new Error(errorData.error || "Errore sconosciuto durante la modifica della prenotazione.");
			}

			const data = await risposta.json();
			mostraNotifica("Prenotazione modificata con successo.", "success");
			return data;
			
			attivaPulsanti(false); // Riabilita i pulsanti Conferma e cancella

		} catch (error) {
			console.error("Errore durante la modifica della prenotazione:", error);
			mostraNotifica("Errore di rete o server non raggiungibile. Riprova più tardi.", "error");
		}
	};


	// Invio dati per cancellare la prenotazione
	const cancellaPrenotazione = async (bookingCode) => {
		if (!bookingCode) {
			console.error("Codice prenotazione mancante.");
			mostraNotifica("Codice prenotazione non fornito.", "error");
			return { success: false, error: "Codice prenotazione mancante." };
		}
			
		try {
			const risposta = await fetch(`/api/prenotazioni/${bookingCode}`, { method: "DELETE" });
	
			if (!risposta.ok) {
				if (risposta.status === 404) {
					mostraNotifica("Prenotazione non trovata.", "error");
					return { success: false, error: "Prenotazione non trovata." };
				}
				const errorData = await risposta.json();
				throw new Error(errorData.error || `Errore HTTP: ${risposta.status}`);
			}
	
			mostraNotifica("Prenotazione cancellata con successo.", "success");
			return { success: true };
	
		} catch (error) {
			console.error("Errore durante la cancellazione della prenotazione:", error);
			mostraNotifica("Errore di rete o server non raggiungibile. Riprova più tardi.", "error");
			return { success: false, error: error.message };
		}
	};



	// Evento click pulsante conferma
	confermaPulsante.addEventListener("click", async (event) => {
		event.preventDefault();

		if (validareForm()) {
			const datiPrenotazione = {
				ritiro_nome: document.getElementById("ritiro_nome").value.trim(),
				ritiro_email: document.getElementById("ritiro_email").value.trim(),
				ritiro_telefono: document.getElementById("ritiro_telefono").value.trim(),
				citta: document.getElementById("citta").value,
				ritiro_indirizzo: document.getElementById("ritiro_indirizzo").value.trim(),
				ritiro_dataora: document.getElementById("ritiro_dataora").value,
				consegna_nome: document.getElementById("consegna_nome").value.trim(),
				consegna_email: document.getElementById("consegna_email").value.trim(),
				consegna_telefono: document.getElementById("consegna_telefono").value.trim(),
				consegna_indirizzo: document.getElementById("consegna_indirizzo").value.trim(),
				peso_pacco: parseFloat(document.getElementById("peso_pacco").value),
			};

			await inviaPrenotazione(datiPrenotazione);
			resettaForm();
		}
	});

	// Evento click pulsante modifica
	modificaPulsante.addEventListener("click", async (event) => {
		event.preventDefault();
		
		
		if (!codicePrenotazioneCorrente) {
        const bookingCode = prompt("Inserisci il codice prenotazione da modificare:");
        if (!bookingCode) {
            mostraNotifica("Codice prenotazione non fornito.", "info");
            return; // Interrompi se non viene fornito un codice
        }
		
		    
		// Recupera i dati della prenotazione dal server
        try {
            const risposta = await fetch(`/api/prenotazioni/${bookingCode}`);
            if (!risposta.ok) {
                mostraNotifica("Codice prenotazione non trovato.", "error");
                return;
            }

            const booking = await risposta.json();

            // Popola i campi del form con i dati della prenotazione recuperata
            document.getElementById("ritiro_nome").value = booking.ritiro_nome;
            document.getElementById("ritiro_email").value = booking.ritiro_email;
            document.getElementById("ritiro_telefono").value = booking.ritiro_telefono;
            document.getElementById("citta").value = booking.citta;
            document.getElementById("ritiro_indirizzo").value = booking.ritiro_indirizzo;
            document.getElementById("ritiro_dataora").value = booking.ritiro_dataora;
            document.getElementById("consegna_nome").value = booking.consegna_nome;
            document.getElementById("consegna_email").value = booking.consegna_email;
            document.getElementById("consegna_telefono").value = booking.consegna_telefono;
            document.getElementById("consegna_indirizzo").value = booking.consegna_indirizzo;
            document.getElementById("peso_pacco").value = booking.peso_pacco;

            codicePrenotazioneCorrente = bookingCode; // Salva il codice per ulteriori modifiche
            mostraNotifica("Modifica i dati e clicca nuovamente su 'Modifica Prenotazione' per confermare.", "info");
			
        } catch (error) {
            console.error("Errore durante il recupero della prenotazione:", error);
            mostraNotifica("Errore durante il recupero della prenotazione.", "error");
        } finally {
			attivaPulsanti(true);
			}
        return; 
    }

		
		if (codicePrenotazioneCorrente) {
			if (validareForm()) {
				const updatedData = {
					ritiro_nome: document.getElementById("ritiro_nome").value.trim(),
					ritiro_email: document.getElementById("ritiro_email").value.trim(),
					ritiro_telefono: document.getElementById("ritiro_telefono").value.trim(),
					citta: document.getElementById("citta").value,
					ritiro_indirizzo: document.getElementById("ritiro_indirizzo").value.trim(),
					ritiro_dataora: document.getElementById("ritiro_dataora").value,
					consegna_nome: document.getElementById("consegna_nome").value.trim(),
					consegna_email: document.getElementById("consegna_email").value.trim(),
					consegna_telefono: document.getElementById("consegna_telefono").value.trim(),
					consegna_indirizzo: document.getElementById("consegna_indirizzo").value.trim(),
					peso_pacco: parseFloat(document.getElementById("peso_pacco").value),
				};

				await modificaPrenotazione(codicePrenotazioneCorrente, updatedData);
				resettaForm();
			}
		} else {
			mostraNotifica("Inserisci un codice di prenotazione valido per la modifica.", "info");
		}
	});
	
	// Evento click pulsante cancella
	cancellaPulsante.addEventListener("click", async (event) => {
		event.preventDefault();
	
		
		const bookingCode = prompt("Inserisci il codice prenotazione da cancellare:");
		if (!bookingCode) {
			mostraNotifica("Codice prenotazione non fornito.", "info");
			return;
		}
	
		// Conferma la cancellazione
		const confirmDelete = confirm(`Sei sicuro di voler cancellare la prenotazione con codice ${bookingCode}?`);
		if (!confirmDelete) {
			return;
		}
	
		// Gestisci la cancellazione
		try {
			cancellaPulsante.disabled = true; 
			const risposta = await cancellaPrenotazione(bookingCode);
			if (risposta.success) {
				resettaForm();
			}
		} catch (error) {
			console.error("Errore durante la cancellazione della prenotazione:", error);
			mostraNotifica("Errore imprevisto. Riprova più tardi.", "error");
		} finally {
			cancellaPulsante.disabled = false; 
		}
	});
	
});