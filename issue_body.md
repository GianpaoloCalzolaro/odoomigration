## Summary

Il modulo **crm_add_field** è un modulo relativamente semplice (2 modelli, 4 viste XML, 1 file dati, 1 file security) che estende il CRM con campi di classificazione aziendale. La migrazione da Odoo 18 a 19 presenta una complessità **bassa-media**. I principali interventi riguardano: la sostituzione di `read_group` con `_read_group` (API deprecata in v19), la rimozione dell'uso di `modifiers` JSON nelle viste XML a favore della sintassi inline, e l'aggiornamento del versioning nel manifest. Non sono presenti asset JavaScript, template QWeb, cron job, né chiamate all'API mail.

---

## Prerequisites

- [ ] Verificare che i moduli `base` e `crm` siano disponibili e funzionanti in Odoo 19
- [ ] Verificare che il gruppo `sales_team.group_sale_manager` e `sales_team.group_sale_salesman` esistano ancora in Odoo 19 (in v18 il modulo `sales_team` è stato in parte riorganizzato; confermare che gli xmlid siano invariati)
- [ ] Verificare che la vista `crm.crm_lead_view_form` e il filtro `crm.view_crm_case_opportunities_filter` non abbiano subito ristrutturazioni significative in v19 che invalidino gli xpath usati dal modulo
- [ ] Verificare che l'action `crm.crm_lead_all_leads` esista ancora in Odoo 19 (usata in `business_sector.py`)
- [ ] Verificare che il campo `tag_ids` e il filtro `source` esistano ancora nella search view CRM di v19 (target degli xpath in `crm_lead_views.xml`)

---

## Changes Required

### Manifest

1. **`__manifest__.py`** — Aggiornare la versione del modulo da `18.0.1.0.0` a `19.0.1.0.0`

### Models

2. **`models/business_sector.py`** — Metodo `_compute_lead_count`: sostituire la chiamata `self.env['crm.lead'].read_group(...)` con `self.env['crm.lead']._read_group(...)` adeguando la signature al nuovo formato introdotto in v17 e reso obbligatorio in v19. Il nuovo metodo accetta `domain, groupby, aggregates` e restituisce direttamente i risultati aggregati. Adattare il parsing del risultato di conseguenza.

3. **`models/business_sector.py`** — Decoratore `@api.depends()`: il decoratore è vuoto, il che significa che il campo computed non viene mai ricalcolato automaticamente. Valutare se aggiungere un trigger esplicito (ad esempio tramite un campo reverse `lead_ids` di tipo One2many) oppure documentare che il valore è calcolato solo on-demand. Questo non è un problema specifico di v19 ma è una best practice da correggere.

4. **`models/business_sector.py`** — Verificare che l'uso di `self.env["ir.actions.actions"]._for_xml_id(...)` sia ancora il pattern corretto in v19. In alcune versioni recenti il metodo preferito è `self.env.ref(xmlid)`.

5. **`models/crm_lead.py`** — Verificare che il campo `annual_volume` con `widget="monetary"` nella vista funzioni correttamente senza un campo `currency_id` esplicitamente definito o ereditato. In v19 il widget monetary potrebbe richiedere un campo currency più rigoroso.

### Views

6. **`views/business_sector_views.xml`** — Nel form view (`view_business_sector_form`), il bottone `action_view_leads` usa la sintassi legacy `modifiers='{"invisible": [["lead_count", "=", 0]]}'`. Sostituire con l'attributo inline `invisible="lead_count == 0"` e rimuovere completamente l'attributo `modifiers`.

7. **`views/business_sector_views.xml`** — Rimuovere l'attributo `string="Business Sectors"` dall'elemento `<list>` nel tree view se non necessario (in v19 il titolo è gestito dall'action, non dalla vista).

8. **`views/business_sector_views.xml`** — L'attributo `<field name="type">search</field>` nella search view è deprecato; in v19 il tipo della vista è determinato automaticamente dall'architettura. Rimuovere la riga.

9. **`views/crm_lead_views.xml`** — Verificare che l'xpath `//notebook` nella form view di `crm.lead` sia ancora un target valido in v19. Se la struttura della form view CRM è cambiata, potrebbe essere necessario aggiornare l'espressione xpath.

10. **`views/crm_lead_views.xml`** — Verificare che gli xpath `//field[@name='tag_ids']` e `//filter[@name='source']` siano ancora validi nella search view CRM di v19. Se i nomi dei filtri o dei campi sono stati riorganizzati, aggiornare i target.

### Security

11. **`security/ir.model.access.csv`** — Verificare che gli xmlid `sales_team.group_sale_manager` e `sales_team.group_sale_salesman` siano ancora validi in Odoo 19. Se il modulo `sales_team` è stato rinominato o i gruppi riorganizzati, aggiornare i riferimenti.

### Data

12. **`data/business_sector_data.xml`** — Nessuna modifica necessaria. I record usano `noupdate="1"` correttamente. Gli xmlid sono specifici del modulo e non creano conflitti.

### Migrations

13. **Nessuno script di migrazione** è strettamente necessario. I campi aggiunti dal modulo sono tutti nuovi e non rinominano né rimuovono campi esistenti. Se il modulo era già installato in v18, i dati verranno preservati automaticamente dall'upgrade. Valutare un pre-migration script solo se si decide di rinominare campi.

### Ulteriori verifiche

14. **i18n** — Rigenerare il file `.pot` e aggiornare il file `it_it.po` dopo le modifiche, per garantire che le traduzioni siano allineate.

15. **Nessun pattern deprecato critico trovato**: il modulo non usa `@api.multi`, `fields.related` con `store=False`, `_name = False`, riferimenti a `ir.values`, `attrs` (tranne il `modifiers` segnalato al punto 6), `sudo()`, cron, template QWeb, componenti OWL, o chiamate `message_post`.
