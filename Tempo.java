package org.example;

import javax.persistence.*;

@Entity
public class Tempo {
    @Id
    @GeneratedValue
    private Long id;

    private String data;
    private int mes;
    private int ano;

    // Getters e Setters
    public Long getId() { return id; }
    public String getData() { return data; }
    public void setData(String data) { this.data = data; }
    public int getMes() { return mes; }
    public void setMes(int mes) { this.mes = mes; }
    public int getAno() { return ano; }
    public void setAno(int ano) { this.ano = ano; }
}