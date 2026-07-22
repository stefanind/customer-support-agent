---
doc_id: KB-SHIP-001
title: Shipping and Delivery Policy
category: shipping
products:
  - all
locale: en-US
version: "1.0.0"
effective_date: "2026-01-15"
access_level: public
---

# Shipping and Delivery Policy

## Scope
<!-- section_id: KB-SHIP-001-scope -->

This policy applies to orders placed directly through the Acme Audio United States online store. Acme Audio currently ships to the 50 United States, the District of Columbia, and APO/FPO/DPO addresses. Orders placed with another retailer follow that retailer's shipping policy.

## Processing Time
<!-- section_id: KB-SHIP-001-processing-time -->

- In-stock orders normally need one business day for warehouse processing before carrier acceptance.
- An order submitted before 2:00 p.m. Eastern Time on a business day may begin processing that business day. An order submitted at exactly 2:00 p.m. Eastern Time or later begins processing on the next business day.
- An order submitted on a Saturday, Sunday, or Acme Audio-observed holiday begins processing on the next business day, regardless of the time submitted.
- Monday through Friday are business days. Saturdays, Sundays, and Acme Audio-observed holidays are not business days.
- A delivery estimate starts after carrier acceptance, not when the order is submitted.
- Preorder and backorder dates shown on the product or order page replace the normal processing estimate.

The approved Acme Audio holiday calendar is authoritative. If a processing date, delivery estimate, or deadline depends on whether a date is an observed holiday and that calendar is unavailable, the automated agent must return `NEEDS_REVIEW` and use the secure support handoff. It must not guess whether the date is a business day.

An order may be cancelled only while its status is `PROCESSING` and before the warehouse lock is recorded. Address changes have the same cutoff. Acme Audio cannot cancel, edit, or reroute an order once its status is `PACKED` or `SHIPPED`.

The Version 1 automated agent cannot cancel an order, change an address, or reroute a shipment. Even before the cutoff, it must use the secure support handoff and must not say that a requested change succeeded. Starting a handoff does not reserve the order's status or extend the warehouse cutoff.

## Shipping Services and Charges
<!-- section_id: KB-SHIP-001-services-and-charges -->

| Service | Delivery estimate after carrier acceptance | Charge |
| --- | --- | --- |
| Standard | 3–5 business days | Free when the merchandise subtotal is at least $75.00; otherwise $6.95 |
| Two-Day | 2 business days | Shown at checkout |
| Next-Day | 1 business day | Shown at checkout |
| APO/FPO/DPO Standard | 7–14 business days | $6.95 |

The merchandise subtotal is calculated after discounts and before tax or shipping. An order with a merchandise subtotal of exactly $75.00 qualifies for free standard shipping. Expedited services are not available for P.O. boxes or APO/FPO/DPO addresses.

Delivery dates are estimates rather than guarantees. Weather, carrier disruptions, and address problems can extend them.

## Tracking and Delivery Problems
<!-- section_id: KB-SHIP-001-tracking-and-delivery-problems -->

Tracking can take up to 24 hours after carrier acceptance to show its first scan. Support may open a carrier trace when either condition is true:

1. tracking has had no new scan for five consecutive calendar days; or
2. the shipment is still undelivered two business days after the carrier's latest estimated delivery date.

For the no-scan rule, the trusted carrier's last-scan date is day 0. Five complete no-scan dates, days 1 through 5, must pass; a trace becomes eligible at 12:00:00 a.m. Eastern Time on day 6. For the late-delivery rule, the carrier's trusted latest estimated-delivery date is day 0. Two complete business days, days 1 and 2, must pass; a trace becomes eligible at 12:00:00 a.m. Eastern Time on the following business day. If an observed holiday affects that calculation and the approved holiday calendar is unavailable, the result is `NEEDS_REVIEW`.

If tracking says `DELIVERED`, the customer should check household members, the delivery area, and any carrier notice, then wait through 11:59:59 p.m. Eastern Time on the next calendar date. If the package is still missing, the customer must report it no later than 11:59:59 p.m. Eastern Time on the date 14 calendar days after the trusted `DELIVERED` scan date. The scan date is day 0, day 14 is timely, and day 15 is late. Support verifies authenticated order ownership before disclosing shipment details or opening a trace.

The Version 1 automated agent may read an authenticated customer's shipment, explain these thresholds, and determine whether a threshold is met from trusted carrier data. Opening a carrier trace or delivery-problem case is an external write and is not supported. The agent must use the secure support handoff and must not claim that a trace or case was opened.

## Damaged, Missing, or Incorrect Shipments
<!-- section_id: KB-SHIP-001-damaged-missing-or-incorrect -->

A visibly damaged package, a missing item, or an incorrect item should be reported no later than 11:59:59 p.m. Eastern Time on the date seven calendar days after the affected order line's trusted carrier delivery date. That delivery date is day 0, day 7 is timely, and day 8 is late. The customer should keep the packaging and provide photos through the approved secure upload when requested. Support compares the report with the shipment record before offering a replacement, refund review, or prepaid return label.

A final-sale designation does not prevent escalation when Acme Audio shipped an incorrect item or the item arrived damaged. It does not automatically guarantee a refund; support must verify the shipment and route the case for review.

The Version 1 automated agent cannot issue a replacement, refund, label, or shipment-error case. It must prepare a secure handoff for those actions and must not promise the outcome.

## Address and Ownership Boundaries
<!-- section_id: KB-SHIP-001-address-and-ownership -->

Support can discuss general shipping policy without authentication. Tracking details, destination information, carrier traces, cancellations, and address-change requests require verified ownership under the Account and Order Help policy. Support must not reveal whether an order exists when ownership cannot be verified.

The Version 1 automated agent can read shipment details only when the trusted authenticated session supplies the owning customer ID. Guest-order verification and any request involving a gift recipient require the secure support handoff; information typed in chat is not verification.

International forwarding services are used at the customer's risk. Acme Audio's delivery responsibility ends at the confirmed United States forwarding address, and Acme Audio does not reimburse forwarding fees or international duties.

## Related Documents
<!-- section_id: KB-SHIP-001-related-documents -->

- `KB-ORD-001` — Account and Order Help
- `KB-RET-001` — Returns and Refunds Policy
