package com.example;

import java.math.BigDecimal;

/** Plain POJO. Default serialization: {"amount":150.00,"currency":"EUR"} */
public class Money {
    private final BigDecimal amount;
    private final String currency;

    public Money(BigDecimal amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }

    public BigDecimal getAmount() { return amount; }
    public String getCurrency() { return currency; }
}
